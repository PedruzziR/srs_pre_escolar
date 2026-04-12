import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import gspread
from google.oauth2.service_account import Credentials
import datetime

# ================= CONFIGURAÇÕES DE E-MAIL =================
SEU_EMAIL = st.secrets["EMAIL_USUARIO"]
SENHA_DO_EMAIL = st.secrets["SENHA_USUARIO"]
EMAIL_DESTINO = "psicologabrunaligoski@gmail.com"
# ===========================================================

# ================= CONEXÃO COM GOOGLE SHEETS =================
@st.cache_resource
def conectar_planilha():
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS_JSON"])
    escopos = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=escopos)
    client = gspread.authorize(creds)
    # CONECTA DIRETAMENTE À PLANILHA DE CONTROLE DE TOKENS
    return client.open("Controle_Tokens").sheet1 

try:
    planilha = conectar_planilha()
except Exception as e:
    st.error(f"Erro de conexão com a planilha de controle: {e}")
    st.stop()
# =============================================================

def enviar_email_resultados(dados_crianca, dados_respondente, resultados_brutos, token):
    assunto = f"Resultados SRS-2 (Pré-Escolar) - Paciente: {dados_crianca['nome']}"
    
    corpo = f"Avaliação SRS-2 (Formulário Pré-Escolar) concluída.\n\n"
    corpo += f"=== DADOS DO(A) PACIENTE ===\n"
    corpo += f"Nome: {dados_crianca['nome']}\n"
    corpo += f"Data de Nascimento: {dados_crianca['data_nasc']}\n"
    corpo += f"Token de Validação: {token}\n\n"
    
    corpo += f"=== DADOS DO(A) RESPONDENTE ===\n\n"
    corpo += f"Nome: {dados_respondente['nome']}\n"
    corpo += f"Vínculo de Parentesco: {dados_respondente['vinculo']}\n\n"
    
    corpo += "================ GABARITO DE RESPOSTAS ================\n"
    corpo += "Formato: [Número da Questão] - [Valor da Resposta]\n\n"
    
    for num_q, valor in resultados_brutos.items():
        corpo += f"{num_q} - {valor}\n"

    msg = MIMEMultipart()
    msg['From'] = SEU_EMAIL
    msg['To'] = EMAIL_DESTINO
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SEU_EMAIL, SENHA_DO_EMAIL)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

# ================= QUESTIONÁRIO =================
perguntas = [
    "Parece muito mais inquieta em situações sociais do que quando está sozinha.",
    "As expressões em seu rosto não combinam com o que está dizendo.",
    "Parece confiante (ou segura) quando está interagindo com outras pessoas.",
    "Quando há sobrecarga de estímulos, a criança parece se desligar do ambiente, apresentando padrões rígidos e inflexíveis de comportamento, aparentemente estranhos.",
    "Não percebe quando os outros estão tentando tirar vantagem dela.",
    "Prefere estar sozinha do que com os outros.",
    "Demonstra perceber o que os outros estão pensando ou sentindo.",
    "Se comporta de maneira estranha ou bizarra.",
    "Fica próxima a adultos, parece ser muito dependente deles.",
    "É incapaz de compreender o sentido da conversa de crianças mais velhas ou adultos.",
    "É autoconfiante.",
    "É capaz de comunicar seus sentimentos a outras pessoas com gestos e palavras.",
    "É devagar ou não consegue interagir com os colegas.",
    "Não tem boa coordenação nas atividades motoras.",
    "É capaz de entender o tom de voz e as expressões faciais das outras pessoas.",
    "Evita o contato visual ou tem contato visual diferente.",
    "Reconhece quando algo é injusto.",
    "Quando está no parquinho ou em um grupo com outras crianças pequenas, não tenta interagir com elas.",
    "Fica frustrada quando não consegue expressar suas ideias em uma conversa.",
    "Tem um jeito estranho de brincar com brinquedos.",
    "É capaz de imitar as ações de outras pessoas.",
    "Brinca adequadamente com crianças da sua idade.",
    "Não participa de atividades em grupo a menos que seja convidada a fazê-lo.",
    "Tem mais dificuldade do que outras crianças com mudanças na sua rotina.",
    "Não parece se importar em estar fora de sintonia ou em um \"mundo\" diferente dos outros.",
    "Oferece conforto para os outros quando estão tristes.",
    "Evita iniciar interações sociais com seus colegas ou adultos.",
    "Pensa ou fala sobre a mesma coisa repetidamente.",
    "É considerada como estranha ou esquisita por outras crianças.",
    "Fica perturbada em uma situação com muitas coisas acontecendo.",
    "Não consegue tirar algo da sua mente uma vez que começa a pensar sobre isso.",
    "Quer ser trocada quando a fralda ou a cueca/calcinha está suja ou molhada.",
    "É socialmente inadequada, mesmo quando tenta ser educada.",
    "Evita pessoas que querem se aproximar dela por meio de contato afetivo.",
    "Tem dificuldade em manter uma interação normal com outras crianças.",
    "Tem dificuldade em se relacionar com adultos.",
    "Tem dificuldade em se relacionar com seus colegas.",
    "Responde adequadamente às mudanças de humor dos outros (por exemplo, quando o humor de um amigo ou companheiro muda de feliz para triste).",
    "Tem uma variedade de interesses extraordinariamente incomuns.",
    "É imaginativa, hábil em fantasiar (contudo sem perder contato com a realidade).",
    "Muda de uma atividade para outra sem objetivo aparente.",
    "Parece excessivamente sensível aos sons, texturas ou cheiros.",
    "Separa-se facilmente (ou frequentemente) dos cuidadores.",
    "Não entende como os eventos se encadeiam, se sucedem, da mesma forma que outras crianças da sua idade o fazem.",
    "Focaliza (ou dirige) sua atenção para onde os outros estão olhando ou ouvindo.",
    "Tem expressão facial excessivamente séria.",
    "Comporta-se como tola ou ri de forma inadequada.",
    "Tem senso de humor e entende as piadas.",
    "É extremamente hábil em algumas tarefas específicas, mas não é tão boa em outras tarefas.",
    "Tem comportamentos repetitivos, estranhos, tais como agitar as mãos ou balançar o corpo fora de contexto.",
    "Responde a questões claras e diretas de maneira que não parecem fazer nenhum sentido.",
    "Sabe quando está falando muito alto ou fazendo muito barulho.",
    "Fala com as pessoas com um tom de voz incomum (por exemplo, fala como um robô ou como se estivesse dando uma palestra).",
    "Parece agir com as pessoas como se elas fossem objetos.",
    "Sabe quando está muito próxima ou invadindo o espaço de alguém.",
    "Caminha entre duas pessoas que estão conversando.",
    "Outras crianças não gostam de brincar com ela.",
    "Concentra-se muito nos detalhes das coisas ao invés de ver o todo. Por exemplo, gira as rodas de um carrinho, mas não brinca como se fosse um carro, ou brinca com o cabelo de uma boneca, mas não com ela toda.",
    "É excessivamente desconfiada.",
    "É emocionalmente distante, não demonstrando seus sentimentos.",
    "É inflexível, leva muito tempo para mudar suas ideias.",
    "Dá explicações incomuns ou ilógicas do porquê de fazer as coisas.",
    "Toca os outros de maneira incomum (por exemplo, pode tocar em alguém apenas para fazer contato e depois ir embora sem dizer nada).",
    "Fica muito agitada em situações sociais.",
    "Fica com olhar perdido ou olha fixamente para o nada."
]

opcoes_respostas = {
    "1 = Não é verdade": 1,
    "2 = Algumas vezes é verdade": 2,
    "3 = Muitas vezes é verdade": 3,
    "4 = Quase sempre é verdade": 4
}

st.set_page_config(page_title="SRS-2 Formulário Pré-Escolar", layout="centered")

# CSS para Botão Azul Forçado
st.markdown("""
    <style>
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #0047AB !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 2.5rem !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #003380 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

if "avaliacao_concluida" not in st.session_state:
    st.session_state.avaliacao_concluida = False

# Título Centralizado
st.markdown("<h1 style='text-align: center;'>Clínica de Psicologia e Psicanálise Bruna Ligoski</h1>", unsafe_allow_html=True)

if st.session_state.avaliacao_concluida:
    st.success("Avaliação concluída e enviada com sucesso! Muito obrigado(a) pela sua colaboração.")
    st.stop()

# ================= VALIDAÇÃO SILENCIOSA DO TOKEN =================
parametros = st.query_params
token_url = parametros.get("token", None)

if not token_url:
    st.warning("⚠️ Link de acesso inválido. Solicite um novo link à profissional.")
    st.stop()

try:
    registros = planilha.get_all_records()
    dados_token = None
    linha_alvo = 2 
    for i, reg in enumerate(registros):
        if str(reg.get("Token")) == token_url:
            dados_token = reg
            linha_alvo += i
            break
            
    if not dados_token or dados_token.get("Status") != "Aberto":
        st.error("⚠️ Este link é inválido ou já foi utilizado.")
        st.stop()
except Exception:
    st.error("Erro técnico na validação do link.")
    st.stop()

# ================= INTERFACE DO TESTE =================
linha_fina = "<hr style='margin-top: 8px; margin-bottom: 8px;'/>"
st.markdown(linha_fina, unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Escala de Responsividade Social (SRS-2) - Pré-Escolar</h3>", unsafe_allow_html=True)
st.markdown(linha_fina, unsafe_allow_html=True)

st.info("**Instruções:** Em cada questão, por favor selecione a alternativa que melhor descreva o comportamento do(a) paciente nos últimos 6 meses.")

with st.form("form_srs2"):
    st.subheader("Dados do(a) Paciente")
    nome_crianca = st.text_input("Nome completo do(a) paciente *")
    data_nasc_crianca = st.date_input("Data de nascimento do(a) paciente *", format="DD/MM/YYYY", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today(), value=None)
    
    st.divider()
    st.subheader("Dados do(a) Respondente")
    nome_respondente = st.text_input("Nome completo do(a) respondente *")
    vinculo_respondente = st.text_input("Vínculo / Parentesco (Ex: Pai, Mãe, Avó) *")
    st.divider()

    respostas_coletadas = {}
    for index, texto_pergunta in enumerate(perguntas):
        num_q = index + 1
        st.write(f"**{num_q}. {texto_pergunta}**")
        resposta = st.radio(f"Oculto {num_q}", list(opcoes_respostas.keys()), index=None, label_visibility="collapsed")
        respostas_coletadas[num_q] = opcoes_respostas[resposta] if resposta else None
        st.divider()

    if st.form_submit_button("Enviar Avaliação"):
        questoes_em_branco = [q for q, r in respostas_coletadas.items() if r is None]

        if not nome_crianca or not nome_respondente or not vinculo_respondente or data_nasc_crianca is None:
            st.error("Por favor, preencha todos os dados de identificação.")
        elif questoes_em_branco:
            st.error(f"Por favor, responda todas as perguntas. Faltam {len(questoes_em_branco)} questão(ões).")
        else:
            dados_paciente = {
                "nome": nome_crianca,
                "data_nasc": data_nasc_crianca.strftime("%d/%m/%Y")
            }
            dados_respondente = {
                "nome": nome_respondente,
                "vinculo": vinculo_respondente
            }

            with st.spinner('Enviando avaliação...'):
                if enviar_email_resultados(dados_paciente, dados_respondente, respostas_coletadas, token_url):
                    try:
                        planilha.update_cell(linha_alvo, 5, "Respondido")
                        st.session_state.avaliacao_concluida = True
                        st.rerun()
                    except:
                        st.session_state.avaliacao_concluida = True
                        st.rerun()
                else:
                    st.error("Houve um erro no envio. Tente novamente.")
