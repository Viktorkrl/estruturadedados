from pydantic import BaseModel


class RelatorioOcupacaoItem(BaseModel):
    evento_id: int
    nome: str
    categoria: str
    vagas_totais: int
    vagas_preenchidas: int
    vagas_restantes: int
    taxa_ocupacao_percentual: float
    status_lotacao: str


class RelatorioCategoriaItem(BaseModel):
    categoria: str
    total_eventos: int
    total_vagas: int
    total_inscricoes: int


class RelatorioCursoItem(BaseModel):
    curso: str
    total_participantes: int
    total_inscricoes: int
