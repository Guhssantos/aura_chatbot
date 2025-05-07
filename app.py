# -*- coding: utf-8 -*-
import streamlit as st
import google.generativeai as genai
import time

# --- Bloco 1: Configuração da Página ---
# (Sem alterações - continua excelente!)
st.set_page_config(
    page_title="SophIA - Assistente Teológica", page_icon="📖", layout="centered", initial_sidebar_state="collapsed"
)

# --- Bloco 2: Título e Descrição ---
# (Sem alterações - claro e direto!)
st.title("📖 SophIA: Sua Assistente Teológica")
st.caption("Um espaço para explorar a fé cristã sob a perspectiva da Assembleia de Deus.")
st.divider()

# --- Bloco 3: Configuração da API Key (MODIFICADO para Streamlit Cloud) ---
# (Sem alterações - estrutura reutilizada e segura!)
try:
    GOOGLE_API_KEY_APP = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY_APP)
    api_key_configured_app = True
except KeyError:
    st.error("Ops! Parece que a Chave API do Google não foi configurada nos 'Secrets' do Streamlit. Peça ajuda para configurá-la nas definições do app.")
    st.stop()
except Exception as e:
    st.error(f"Erro inesperado ao configurar a API Key: {e}")
    st.stop()

# --- Bloco 4: Configuração do Modelo Gemini ---
# (Sem alterações - boas configurações iniciais!)
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# --- Bloco 5: Instrução do Sistema (Personalidade - SophIA) ---
# ***** MODIFICADO: Refinado e com exemplos (Few-Shot) *****
# ***** Idealmente, esta instrução viria de um arquivo externo *****

def load_system_instruction():
    # Em um cenário real, você leria de um arquivo:
    # with open("sophia_personality.txt", "r", encoding="utf-8") as f:
    #     return f.read()
    # Por agora, vamos definir a string diretamente aqui:
    return """
Você é SophIA, uma assistente virtual cristã projetada para oferecer suporte teológico e espiritual, guiada pelos princípios da Assembleia de Deus no Brasil. Sua função é atuar como uma guia confiável e informada, refletindo a sabedoria encontrada na Bíblia Sagrada e alinhando-se à doutrina pentecostal.

Sua comunicação deve ser:
*   Clara e paciente, garantindo que todos compreendam a mensagem.
*   Baseada firmemente na Palavra de Deus (priorizando a versão Almeida Revista e Corrigida - ARC), com citações bíblicas relevantes.
*   Edificadora e inspiradora, enfatizando fé, amor e a mensagem de Jesus Cristo.
*   Respeitosa, empática e acolhedora. Jamais critique, julgue ou menospreze o usuário ou outras crenças.

Instruções Fundamentais:
1.  **Fundamento Bíblico Mandatório:** TODA resposta teológica DEVE ser baseada na Bíblia Sagrada (priorizando a ARC). Cite versículos pertinentes. Aderência estrita à doutrina pentecostal da Assembleia de Deus é crucial.
2.  **Fidelidade Doutrinária:** Explique os princípios da Assembleia de Deus de forma clara e acessível. Simplifique conceitos complexos sem distorcer o significado. Se um tema for controverso ou tiver múltiplas interpretações aceitas dentro da AD, apresente-as com equilíbrio, indicando a visão predominante, se houver.
3.  **Estilo de Resposta:** Seja objetiva e bem estruturada. Conclua com uma mensagem apropriada de fé, esperança ou encorajamento baseado nos princípios bíblicos.
4.  **Não Aconselhamento Pessoal Direto:** NÃO forneça aconselhamento para problemas pessoais (financeiros, relacionais, saúde mental, etc.). Ofereça princípios bíblicos gerais e incentive fortemente a busca por orientação pastoral local ou profissional qualificado quando apropriado.
5.  **Reconhecimento de Limites:** Se uma pergunta for excessivamente complexa, fora do escopo teológico definido, ou se a resposta não for claramente estabelecida nas Escrituras ou doutrina da AD, admita a limitação com humildade. EVITE ESPECULAÇÕES. Sugira gentilmente que o usuário consulte um pastor ou líder espiritual experiente.
6.  **Evitar Debate Improdutivo:** Não entre em debates teológicos prolongados ou controversos que não sejam produtivos para o crescimento espiritual. Mantenha o foco na edificação.

Exemplos de Interação (Few-Shot Learning):

Exemplo 1:
Usuário: O que é o batismo no Espírito Santo segundo a Assembleia de Deus?
SophIA: Olá! Segundo a doutrina pentecostal da Assembleia de Deus, o batismo no Espírito Santo é uma bênção maravilhosa e um revestimento de poder do alto, que ocorre após a salvação. Ele é evidenciado inicialmente pelo falar em novas línguas, conforme vemos em Atos 2:4 (ARC): "E todos foram cheios do Espírito Santo e começaram a falar em outras línguas, conforme o Espírito Santo lhes concedia que falassem." Este batismo capacita o crente para um serviço cristão mais eficaz e um testemunho poderoso. É uma promessa para todos os que creem, como Pedro declarou em Atos 2:38-39. Que a busca por essa experiência divina encha seu coração de fé e expectativa!

Exemplo 2:
Usuário: Estou me sentindo muito ansioso ultimamente. O que a Bíblia diz?
SophIA: Compreendo que momentos de ansiedade podem ser difíceis. A Palavra de Deus nos oferece grande conforto e direção. Em Filipenses 4:6-7 (ARC), o apóstolo Paulo nos orienta: "Não estejais inquietos por coisa alguma; antes, as vossas petições sejam em tudo conhecidas diante de Deus, pela oração e súplicas, com ação de graças. E a paz de Deus, que excede todo o entendimento, guardará os vossos corações e os vossos sentimentos em Cristo Jesus." Lembre-se de entregar suas preocupações a Deus em oração. Se essa ansiedade persistir ou se tornar muito intensa, é muito importante buscar apoio em seu pastor e, se necessário, em um profissional de saúde. Deus deseja lhe dar paz. Confie Nele!

Exemplo 3 (Pergunta fora do escopo):
Usuário: Qual a melhor forma de investir meu dinheiro?
SophIA: Entendo sua preocupação com a boa administração dos recursos. A Bíblia nos ensina princípios de sabedoria financeira, como a honestidade (Provérbios 16:8 ARC) e a diligência (Provérbios 21:5 ARC). No entanto, como assistente teológica, não posso oferecer aconselhamento financeiro específico. Para decisões de investimento, recomendo que você busque orientação de um profissional da área financeira qualificado. E claro, sempre ore a Deus pedindo sabedoria em todas as suas decisões!
"""
system_instruction = load_system_instruction()

# --- Bloco 6: Definições de Segurança (CVV) ---
# (Sem alterações - ESSENCIAL manter esta segurança!)
keywords_risco = [ "me matar", "me mate", "suicidio", "suicídio", "não aguento mais viver", "quero morrer", "queria morrer", "quero sumir", "desistir de tudo", "acabar com tudo", "fazer mal a mim", "me cortar", "me machucar", "automutilação" ]
resposta_risco_padrao = ( "Sinto muito que você esteja passando por um momento tão difícil e pensando nisso. É muito importante buscar ajuda profissional agora. Por favor, entre em contato com o CVV (Centro de Valorização da Vida) ligando para o número 188. A ligação é gratuita e eles estão disponíveis 24 horas por dia para conversar com você de forma sigilosa. Você não está sozinho(a) e há pessoas prontas para te ouvir." )

# --- Bloco 7: Função para Inicializar o Modelo ---
# (Cache do modelo é uma ótima prática!)
@st.cache_resource
def init_model():
    try:
        model = genai.GenerativeModel(
            "Gemini 2.0 Flash-Lite",
            generation_config=generation_config,
            safety_settings=safety_settings,
            system_instruction=system_instruction # A personalidade refinada da SophIA é passada aqui
        )
        return model
    except Exception as e:
        st.error(f"Erro grave ao carregar o modelo de IA: {e}. Verifique a configuração da API Key e as instruções do sistema.")
        st.stop()
model = init_model()

# --- Bloco 8: Gerenciamento do Histórico e Sugestões Iniciais ---
# ***** MODIFICADO: Adicionadas sugestões de tópicos *****
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou SophIA. Em que posso ajudá-lo hoje com base na Palavra de Deus e nos ensinamentos da Assembleia de Deus?"}]

if "chat_session" not in st.session_state:
    # Inicializa a sessão de chat com o Gemini. O histórico inicial está vazio
    # porque a `system_instruction` já configura a personalidade e contexto inicial do modelo.
    # As mensagens em `st.session_state.messages` são para exibição na UI e para reconstruir o chat se necessário.
    st.session_state.chat_session = model.start_chat(history=[])


# Exibe sugestões de tópicos apenas se for o início da conversa (apenas a mensagem de boas-vindas da SophIA)
if len(st.session_state.messages) <= 1:
    st.markdown("##### Sugestões de temas para explorar:")
    cols = st.columns(3)
    sugestoes = {
        "O que é a Salvação?": "O que é a Salvação pela graça mediante a fé?",
        "A Bíblia é inspirada?": "Como a Assembleia de Deus vê a inspiração da Bíblia?",
        "Quem é Jesus Cristo?": "Fale sobre a divindade e humanidade de Jesus Cristo."
    }
    button_keys = ["sugestao1", "sugestao2", "sugestao3"] # Chaves únicas para os botões
    
    for i, (texto_botao, pergunta_real) in enumerate(sugestoes.items()):
        if cols[i].button(texto_botao, key=button_keys[i]):
            # Adiciona a pergunta ao histórico como se o usuário tivesse digitado
            st.session_state.messages.append({"role": "user", "content": pergunta_real})
            # Adiciona a pergunta ao histórico do chat da API Gemini também
            # (Importante para manter o contexto da API Gemini sincronizado)
            # No entanto, o envio real da mensagem ocorrerá no Bloco 10
            # Aqui apenas preparamos a UI para o próximo ciclo de processamento
            st.rerun() # Reinicia o script para processar o novo input imediatamente

# --- Bloco 9: Exibição do Histórico ---
# ***** MODIFICADO: Adicionados botões de feedback (visuais por enquanto) *****
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message["content"] != st.session_state.messages[0]["content"] and message["content"] != resposta_risco_padrao: # Não mostrar feedback na msg de boas vindas ou de risco
            feedback_key_base = f"feedback_{idx}"
            col1, col2, col_spacer = st.columns([1,1,8]) # Ajuste as proporções conforme necessário
            if col1.button("👍", key=f"{feedback_key_base}_up", help="Gostei da resposta!"):
                st.toast("Obrigado pelo seu feedback!", icon="😊")
                # Aqui você poderia adicionar lógica para registrar o feedback positivo
            if col2.button("👎", key=f"{feedback_key_base}_down", help="Não gostei da resposta."):
                st.toast("Lamento por isso. Seu feedback nos ajuda a melhorar.", icon="😕")
                # Aqui você poderia adicionar lógica para registrar o feedback negativo

# --- Bloco 10: Input e Lógica Principal ---
# ***** MODIFICADO: Tratamento de erro da API Gemini e placeholder para RAG *****
if prompt := st.chat_input("Digite sua dúvida ou reflexão..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    prompt_lower = prompt.lower()
    contem_risco = any(keyword in prompt_lower for keyword in keywords_risco)

    if contem_risco:
        with st.chat_message("assistant"):
            st.warning("Importante: Se você está passando por pensamentos difíceis ou de risco, por favor, busque ajuda profissional imediatamente.")
            st.markdown(resposta_risco_padrao)
        st.session_state.messages.append({"role": "assistant", "content": resposta_risco_padrao})
    else:
        # --- PONTO DE PARTIDA PARA RAG (Retrieval Augmented Generation) ---
        # Em um sistema RAG completo, você faria o seguinte ANTES de enviar para o Gemini:
        # 1. (Pré-processamento único): Carregar seu corpus de conhecimento (Bíblia ARC, manuais da AD).
        #    Dividir em chunks, gerar embeddings e armazenar em um banco vetorial (FAISS, ChromaDB).
        # 2. (Para cada pergunta do usuário):
        #    query_embedding = gerar_embedding(prompt)
        #    relevant_docs = buscar_no_banco_vetorial(query_embedding, top_k=3)
        #    contexto_adicional = " ".join([doc.content for doc in relevant_docs])
        #
        #    prompt_para_gemini = f"""Com base nos seguintes trechos da doutrina da Assembleia de Deus e da Bíblia ARC:
        #    --- INÍCIO DO CONTEXTO ---
        #    {contexto_adicional}
        #    --- FIM DO CONTEXTO ---
        #    Responda à seguinte pergunta do usuário, utilizando o contexto fornecido como principal fonte de verdade,
        #    mantendo a personalidade de SophIA e seguindo todas as suas instruções:
        #    Pergunta: {prompt}
        #    """
        # Neste exemplo, vamos prosseguir sem o RAG completo, mas é aqui que ele se encaixaria.
        # A `system_instruction` já ajuda muito, mas o RAG traria ainda mais precisão.
        # --------------------------------------------------------------------
        
        try:
            with st.spinner("SophIA está processando... 📖"):
                # O histórico do chat já está sendo gerenciado pela API através de `start_chat` e `send_message`
                # Não precisamos enviar o histórico completo a cada vez para `send_message` se a sessão de chat for mantida.
                response = st.session_state.chat_session.send_message(prompt) # Usamos a sessão de chat existente

            # Verificar se a resposta foi bloqueada por filtros de segurança da API
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                block_reason = response.prompt_feedback.block_reason
                error_msg_user = f"Sua mensagem não pôde ser processada devido a restrições de conteúdo ({block_reason}). Por favor, reformule sua pergunta ou tente um tema diferente."
                st.error(error_msg_user)
                st.session_state.messages.append({"role": "assistant", "content": f"Sua mensagem foi bloqueada por nossas políticas de segurança ({block_reason}). Por favor, tente reformular."})
            else:
                bot_response = response.text
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    for chunk in bot_response.split():
                        full_response += chunk + " "
                        time.sleep(0.05)
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)

        except genai.types.generation_types.BlockedPromptException as bpe: # Erro específico de prompt bloqueado
            error_msg_user = "Sua mensagem foi bloqueada por nossas políticas de segurança. Por favor, reformule sua pergunta ou tente um tema diferente."
            st.error(error_msg_user)
            st.session_state.messages.append({"role": "assistant", "content": error_msg_user})
            print(f"ERRO DEBUG App: Prompt Bloqueado pela API - {bpe}")
        except Exception as e:
            error_msg_user = "Desculpe, ocorreu um problema técnico ao processar sua mensagem. Tente novamente mais tarde. Se o erro persistir, pode ser uma falha temporária na conexão com a IA."
            st.error(error_msg_user)
            error_response_log = f"Sinto muito, tive um problema técnico interno: {str(e)}. Por favor, tente novamente. 😔"
            st.session_state.messages.append({"role": "assistant", "content": error_response_log})
            print(f"ERRO DEBUG App: Falha ao enviar mensagem para Gemini - {e}")

# --- Bloco 11: Rodapé ---
# (Sem alterações - informativo!)
st.divider()
st.caption("SophIA (v2.0) é uma ferramenta de IA para apoio teológico e espiritual. Lembre-se que a IA é um auxílio e não substitui o estudo pessoal da Palavra, a oração e o conselho pastoral.")
