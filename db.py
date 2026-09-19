import sqlite3
import json
import uuid
import os
import sys
import hashlib
import secrets
import datetime


def _base_dir() -> str:
    # Quando empacotado com "flet pack" (PyInstaller), sys.frozen é True e
    # o executável fica em sys.executable. Guardamos o banco AO LADO do
    # executável final, não numa pasta temporária que é apagada a cada abertura.
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


DB_PATH = os.path.join(_base_dir(), "medsafe.db")


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS medicamentos (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            apresentacao TEXT,
            alto_risco INTEGER DEFAULT 0,
            favorito INTEGER DEFAULT 0,
            apresentacoes TEXT,
            via_administracao TEXT,
            capacidade_infusao TEXT,
            diluicao TEXT,
            cuidados TEXT,
            interacoes TEXT,
            categoria TEXT DEFAULT '',
            validade TEXT DEFAULT ''
        )
        """
    )
    conn.commit()
    _garantir_colunas(conn, "medicamentos", {"categoria": "TEXT DEFAULT ''", "validade": "TEXT DEFAULT ''"})

    # Semeia com dados de exemplo apenas se a tabela estiver vazia
    total = conn.execute("SELECT COUNT(*) AS c FROM medicamentos").fetchone()["c"]
    if total == 0:
        for m in _SEED:
            _inserir(conn, m)
        conn.commit()

    _init_protocolos(conn)
    _init_config(conn)
    _init_usuarios(conn)
    _init_logs(conn)
    conn.commit()
    conn.close()


def _garantir_colunas(conn, tabela, colunas: dict):
    """Adiciona colunas que ainda não existem, sem apagar dados já salvos."""
    existentes = {row["name"] for row in conn.execute(f"PRAGMA table_info({tabela})")}
    for nome, tipo in colunas.items():
        if nome not in existentes:
            conn.execute(f"ALTER TABLE {tabela} ADD COLUMN {nome} {tipo}")
    conn.commit()



def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for campo in ["apresentacoes", "via_administracao", "cuidados", "interacoes"]:
        d[campo] = json.loads(d[campo] or "[]")
    d["alto_risco"] = bool(d["alto_risco"])
    d["favorito"] = bool(d["favorito"])
    return d


def _inserir(conn, m: dict):
    conn.execute(
        """
        INSERT INTO medicamentos
        (id, nome, apresentacao, alto_risco, favorito, apresentacoes, via_administracao, capacidade_infusao, diluicao, cuidados, interacoes, categoria, validade)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            m["id"],
            m["nome"],
            m.get("apresentacao", ""),
            int(m.get("alto_risco", False)),
            int(m.get("favorito", False)),
            json.dumps(m.get("apresentacoes", []), ensure_ascii=False),
            json.dumps(m.get("via_administracao", []), ensure_ascii=False),
            m.get("capacidade_infusao", ""),
            m.get("diluicao", ""),
            json.dumps(m.get("cuidados", []), ensure_ascii=False),
            json.dumps(m.get("interacoes", []), ensure_ascii=False),
            m.get("categoria", ""),
            m.get("validade", ""),
        ),
    )


def listar(termo: str = "", apenas_favoritos: bool = False, apenas_alto_risco: bool = False,
           categoria: str = "", ordenar_por: str = "nome") -> list:
    conn = _conn()
    query = "SELECT * FROM medicamentos WHERE 1=1"
    params = []
    if termo:
        query += " AND LOWER(nome) LIKE ?"
        params.append(f"%{termo.lower()}%")
    if apenas_favoritos:
        query += " AND favorito = 1"
    if apenas_alto_risco:
        query += " AND alto_risco = 1"
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    coluna_ordem = {"nome": "nome", "recentes": "rowid DESC", "validade": "validade"}.get(ordenar_por, "nome")
    query += f" ORDER BY {coluna_ordem}"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def listar_categorias() -> list:
    conn = _conn()
    rows = conn.execute(
        "SELECT DISTINCT categoria FROM medicamentos WHERE categoria != '' ORDER BY categoria"
    ).fetchall()
    conn.close()
    return [r["categoria"] for r in rows]


def obter(mid: str):
    conn = _conn()
    row = conn.execute("SELECT * FROM medicamentos WHERE id = ?", (mid,)).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def criar(dados: dict, usuario: str = "") -> str:
    novo_id = str(uuid.uuid4())[:8]
    dados = {**dados, "id": novo_id}
    conn = _conn()
    _inserir(conn, dados)
    conn.commit()
    conn.close()
    _registrar_log(usuario, "criar", "medicamento", novo_id, dados.get("nome", ""))
    return novo_id


def atualizar(mid: str, dados: dict, usuario: str = ""):
    conn = _conn()
    conn.execute(
        """
        UPDATE medicamentos SET
            nome = ?, apresentacao = ?, alto_risco = ?,
            apresentacoes = ?, via_administracao = ?, capacidade_infusao = ?,
            diluicao = ?, cuidados = ?, interacoes = ?, categoria = ?, validade = ?
        WHERE id = ?
        """,
        (
            dados["nome"],
            dados.get("apresentacao", ""),
            int(dados.get("alto_risco", False)),
            json.dumps(dados.get("apresentacoes", []), ensure_ascii=False),
            json.dumps(dados.get("via_administracao", []), ensure_ascii=False),
            dados.get("capacidade_infusao", ""),
            dados.get("diluicao", ""),
            json.dumps(dados.get("cuidados", []), ensure_ascii=False),
            json.dumps(dados.get("interacoes", []), ensure_ascii=False),
            dados.get("categoria", ""),
            dados.get("validade", ""),
            mid,
        ),
    )
    conn.commit()
    conn.close()
    _registrar_log(usuario, "editar", "medicamento", mid, dados.get("nome", ""))


def excluir(mid: str, usuario: str = ""):
    m = obter(mid)
    conn = _conn()
    conn.execute("DELETE FROM medicamentos WHERE id = ?", (mid,))
    conn.commit()
    conn.close()
    _registrar_log(usuario, "excluir", "medicamento", mid, m["nome"] if m else mid)


def alternar_favorito(mid: str):
    conn = _conn()
    row = conn.execute("SELECT favorito FROM medicamentos WHERE id = ?", (mid,)).fetchone()
    novo_valor = 0 if row["favorito"] else 1
    conn.execute("UPDATE medicamentos SET favorito = ? WHERE id = ?", (novo_valor, mid))
    conn.commit()
    conn.close()
    return bool(novo_valor)


# ---------- PROTOCOLOS ----------

def _init_protocolos(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS protocolos (
            id TEXT PRIMARY KEY,
            titulo TEXT NOT NULL,
            conteudo TEXT
        )
        """
    )
    total = conn.execute("SELECT COUNT(*) AS c FROM protocolos").fetchone()["c"]
    if total == 0:
        for p in _SEED_PROTOCOLOS:
            conn.execute(
                "INSERT INTO protocolos (id, titulo, conteudo) VALUES (?, ?, ?)",
                (p["id"], p["titulo"], p["conteudo"]),
            )


def listar_protocolos() -> list:
    conn = _conn()
    rows = conn.execute("SELECT * FROM protocolos ORDER BY titulo").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obter_protocolo(pid: str):
    conn = _conn()
    row = conn.execute("SELECT * FROM protocolos WHERE id = ?", (pid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def criar_protocolo(titulo: str, conteudo: str) -> str:
    novo_id = str(uuid.uuid4())[:8]
    conn = _conn()
    conn.execute("INSERT INTO protocolos (id, titulo, conteudo) VALUES (?, ?, ?)", (novo_id, titulo, conteudo))
    conn.commit()
    conn.close()
    return novo_id


def atualizar_protocolo(pid: str, titulo: str, conteudo: str):
    conn = _conn()
    conn.execute("UPDATE protocolos SET titulo = ?, conteudo = ? WHERE id = ?", (titulo, conteudo, pid))
    conn.commit()
    conn.close()


def excluir_protocolo(pid: str):
    conn = _conn()
    conn.execute("DELETE FROM protocolos WHERE id = ?", (pid,))
    conn.commit()
    conn.close()


_SEED_PROTOCOLOS = [
    {
        "id": "adm-medicamentos",
        "titulo": "Administração de medicamentos",
        "conteudo": "Siga sempre os 9 certos: paciente, medicamento, dose, via, horário, registro, orientação, validade e forma de administração.",
    },
    {
        "id": "risco-alto",
        "titulo": "Medicamentos de alto risco",
        "conteudo": "Exigem dupla checagem por dois profissionais antes da administração. Use bomba de infusão sempre que indicado.",
    },
]


# ---------- CONFIGURAÇÕES (chave-valor) ----------

def _init_config(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS config (chave TEXT PRIMARY KEY, valor TEXT)")


def get_config(chave: str, padrao=None):
    conn = _conn()
    row = conn.execute("SELECT valor FROM config WHERE chave = ?", (chave,)).fetchone()
    conn.close()
    return row["valor"] if row else padrao


def set_config(chave: str, valor: str):
    conn = _conn()
    conn.execute("INSERT INTO config (chave, valor) VALUES (?, ?) ON CONFLICT(chave) DO UPDATE SET valor = ?", (chave, valor, valor))
    conn.commit()
    conn.close()


# ---------- USUÁRIOS (login real) ----------

def _init_usuarios(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            email TEXT PRIMARY KEY,
            senha_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            criado_em TEXT
        )
        """
    )


def _hash_senha(senha: str, salt: str) -> str:
    return hashlib.sha256((salt + senha).encode("utf-8")).hexdigest()


def existe_algum_usuario() -> bool:
    conn = _conn()
    total = conn.execute("SELECT COUNT(*) AS c FROM usuarios").fetchone()["c"]
    conn.close()
    return total > 0


def criar_usuario(email: str, senha: str) -> bool:
    """Retorna False se o e-mail já existir."""
    email = email.strip().lower()
    conn = _conn()
    existe = conn.execute("SELECT 1 FROM usuarios WHERE email = ?", (email,)).fetchone()
    if existe:
        conn.close()
        return False
    salt = secrets.token_hex(16)
    conn.execute(
        "INSERT INTO usuarios (email, senha_hash, salt, criado_em) VALUES (?, ?, ?, ?)",
        (email, _hash_senha(senha, salt), salt, datetime.datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    return True


def autenticar(email: str, senha: str) -> bool:
    email = email.strip().lower()
    conn = _conn()
    row = conn.execute("SELECT senha_hash, salt FROM usuarios WHERE email = ?", (email,)).fetchone()
    conn.close()
    if not row:
        return False
    return _hash_senha(senha, row["salt"]) == row["senha_hash"]


# ---------- LOG DE ALTERAÇÕES E HISTÓRICO DE ADMINISTRAÇÃO ----------

def _init_logs(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS log_alteracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT,
            usuario TEXT,
            acao TEXT,
            entidade TEXT,
            entidade_id TEXT,
            detalhe TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS administracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT,
            usuario TEXT,
            detalhe TEXT
        )
        """
    )


def _registrar_log(usuario: str, acao: str, entidade: str, entidade_id: str, detalhe: str):
    conn = _conn()
    conn.execute(
        "INSERT INTO log_alteracoes (data_hora, usuario, acao, entidade, entidade_id, detalhe) VALUES (?, ?, ?, ?, ?, ?)",
        (datetime.datetime.now().isoformat(), usuario or "desconhecido", acao, entidade, entidade_id, detalhe),
    )
    conn.commit()
    conn.close()


def listar_log(limite: int = 50) -> list:
    conn = _conn()
    rows = conn.execute(
        "SELECT * FROM log_alteracoes ORDER BY id DESC LIMIT ?", (limite,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def registrar_administracao(usuario: str, detalhe: str):
    conn = _conn()
    conn.execute(
        "INSERT INTO administracoes (data_hora, usuario, detalhe) VALUES (?, ?, ?)",
        (datetime.datetime.now().isoformat(), usuario or "desconhecido", detalhe),
    )
    conn.commit()
    conn.close()


def listar_administracoes(limite: int = 50) -> list:
    conn = _conn()
    rows = conn.execute(
        "SELECT * FROM administracoes ORDER BY id DESC LIMIT ?", (limite,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- ESTATÍSTICAS ----------

def estatisticas() -> dict:
    conn = _conn()
    total_meds = conn.execute("SELECT COUNT(*) AS c FROM medicamentos").fetchone()["c"]
    alto_risco = conn.execute("SELECT COUNT(*) AS c FROM medicamentos WHERE alto_risco = 1").fetchone()["c"]
    total_protocolos = conn.execute("SELECT COUNT(*) AS c FROM protocolos").fetchone()["c"]
    total_checklists = conn.execute("SELECT COUNT(*) AS c FROM administracoes").fetchone()["c"]
    total_favoritos = conn.execute("SELECT COUNT(*) AS c FROM medicamentos WHERE favorito = 1").fetchone()["c"]
    conn.close()
    return {
        "total_medicamentos": total_meds,
        "alto_risco": alto_risco,
        "total_protocolos": total_protocolos,
        "checklists_concluidos": total_checklists,
        "favoritos": total_favoritos,
    }


# ---------- CHECAGEM CRUZADA DE INTERAÇÕES ----------

def checar_interacoes_cruzadas(ids: list) -> list:
    """Retorna avisos quando o texto de interação de um medicamento menciona
    o nome de outro medicamento selecionado (comparação simples por substring)."""
    meds = [obter(mid) for mid in ids if obter(mid)]
    avisos = []
    for i, m1 in enumerate(meds):
        for m2 in meds:
            if m1["id"] == m2["id"]:
                continue
            for texto in m1["interacoes"]:
                if m2["nome"].lower() in texto.lower():
                    avisos.append(f"{m1['nome']} + {m2['nome']}: {texto}")
    return avisos



_SEED = [
    {
        "id": "dipirona",
        "nome": "Dipirona",
        "apresentacao": "500 mg/mL (gotas)",
        "alto_risco": False,
        "favorito": True,
        "apresentacoes": ["Ampola 1g/2mL", "Comprimido 500mg", "Gotas 500mg/mL"],
        "via_administracao": ["EV (diluída)", "IM profunda", "VO"],
        "capacidade_infusao": "IV em bolus lento ou 30 a 100mL de diluente",
        "cuidados": [
            "Verificar alergia prévia a dipirona",
            "Administrar lentamente em bolus (risco de hipotensão)",
            "Monitorar sinais de reação anafilática",
        ],
        "diluicao": "Diluir 1g em 100mL de SF 0,9% ou SG 5%",
        "interacoes": [
            "Anticoagulantes orais: risco de sangramento aumentado",
            "Clorpromazina: risco de hipotermia severa",
        ],
    },
    {
        "id": "ceftriaxona",
        "nome": "Ceftriaxona",
        "apresentacao": "1g pó para diluição",
        "alto_risco": False,
        "favorito": False,
        "apresentacoes": ["Frasco-ampola 1g"],
        "via_administracao": ["EV", "IM"],
        "capacidade_infusao": "Infundir em 30 minutos, diluído em 50 a 100mL",
        "cuidados": [
            "Não diluir com soluções contendo cálcio (risco de precipitação)",
            "Verificar histórico de alergia a betalactâmicos",
        ],
        "diluicao": "Diluir em SF 0,9% ou AD, conforme apresentação",
        "interacoes": ["Soluções com cálcio (ex: Ringer com lactato) — risco de precipitação"],
    },
    {
        "id": "heparina",
        "nome": "Heparina",
        "apresentacao": "5000 UI/mL",
        "alto_risco": True,
        "favorito": True,
        "apresentacoes": ["Ampola 5.000 UI/mL", "Ampola 25.000 UI/5mL"],
        "via_administracao": ["EV contínua", "SC"],
        "capacidade_infusao": "Conforme protocolo de bomba de infusão (UI/kg/h)",
        "cuidados": [
            "Medicamento de alto risco — dupla checagem obrigatória",
            "Monitorar TTPa e sinais de sangramento",
            "Confirmar dose com prescrição antes de administrar",
        ],
        "diluicao": "Diluir conforme protocolo institucional de bomba de infusão",
        "interacoes": ["AAS e outros anticoagulantes: potencializa risco de sangramento"],
    },
    {
        "id": "kcl",
        "nome": "Cloreto de Potássio (KCl)",
        "apresentacao": "10% ou 19,1%",
        "alto_risco": True,
        "favorito": False,
        "apresentacoes": ["Ampola 10mL a 10%", "Ampola 10mL a 19,1%"],
        "via_administracao": ["EV diluído — NUNCA em bolus"],
        "capacidade_infusao": "Máximo 10 a 20mEq/h, sempre diluído",
        "cuidados": [
            "NUNCA administrar em bolus ou não diluído — risco de parada cardíaca",
            "Medicamento de alto risco — dupla checagem obrigatória",
            "Usar bomba de infusão sempre",
        ],
        "diluicao": "Diluir em no mínimo 100mL de SF 0,9% ou SG 5%",
        "interacoes": ["Digitálicos: risco aumentado de arritmias com distúrbios de potássio"],
    },
]
