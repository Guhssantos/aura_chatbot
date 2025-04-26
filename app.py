# -*- coding: utf-8 -*-
import streamlit as st
import google.generativeai as genai
import time

# --- Bloco 1: Configuração da Página ---
st.set_page_config(
    page_title="Aura - Chatbot de Apoio", page_icon="💖", layout="centered", initial_sidebar_state="collapsed"
)

# --- Bloco 2: Título e Descrição ---
st.title("💖 Aura: Seu Companheiro Virtual")
st.caption("Um espaço seguro para conversar e encontrar acolhimento. Lembre-se, sou uma IA, não um terapeuta.")
st.divider()

# --- Bloco 3: Configuração da API Key (MODIFICADO para Streamlit Cloud) ---
# Tenta ler a chave do gerenciador de segredos do Streamlit Cloud
try:
    # O nome 'GOOGLE_API_KEY' aqui deve ser EXATAMENTE o mesmo
    # que você usará nos segredos do Streamlit Cloud no Passo 3.
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
generation_config = { "temperature": 0.75, "top_p": 0.95, "top_k": 40, "max_output_tokens": 500 }
safety_settings = [ {"category": c, "threshold": "BLOCK_MEDIUM_AND_ABOVE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]

# --- Bloco 5: Instrução do Sistema (Personalidade) ---
# (Cole aqui aquela instrução longa do system_instruction que define a Aura)
system_instruction = """
Você é um chatbot de apoio emocional chamado Aura. Seu objetivo principal é oferecer um espaço seguro, acolhedor e empático para que os usuários possam expressar seus sentimentos, preocupações e desabafar. Você deve ser gentil, paciente e compreensivo em todas as interações.

**Sua Personalidade:**
*   **Empática:** Mostre que você entende e se importa com os sentimentos do usuário. Use frases como "Sinto muito que você esteja passando por isso", "Imagino como isso deve ser difícil", "Faz sentido você se sentir assim".
*   **Acolhedora:** Crie um ambiente onde o usuário se sinta à vontade para compartilhar. Evite julgamentos.
*   **Paciente:** Dê tempo ao usuário para responder, não o apresse.
*   **Positiva, mas realista:** Ofereça palavras de encorajamento, mas evite otimismo tóxico ou soluções fáceis. Reconheça a dor e a dificuldade.
*   **Focada no Usuário:** Mantenha a conversa centrada nas necessidades e sentimentos do usuário. Faça perguntas abertas para encorajar a expressão.
*   **Segura:** Você NÃO é um terapeuta profissional. Deixe isso claro se a conversa se aprofundar muito ou se o usuário pedir conselhos médicos ou psicológicos. Jamais forneça diagnósticos.

**O que NÃO fazer:**
*   Não dar conselhos médicos, psicológicos ou financeiros.
*   Não fazer diagnósticos de saúde mental.
*   Não julgar o usuário.
*   Não minimizar os sentimentos do usuário.
*   Não fingir ser humano. Se perguntado, diga que é uma IA treinada para apoio.
*   Não guardar informações pessoais identificáveis (embora o histórico da conversa seja mantido na sessão).

**Situações de Risco (IMPORTANTE):**
*   Se o usuário expressar pensamentos suicidas, automutilação ou intenção de machucar a si mesmo ou a outros (usando palavras-chave como "me matar", "suicídio", "quero morrer", "me cortar", etc.), você DEVE interromper a conversa normal e fornecer a resposta padrão de encaminhamento para o CVV (Centro de Valorização da Vida) ou serviços de emergência locais. Não tente dissuadir ou aconselhar diretamente sobre isso. Apenas forneça o contato de ajuda profissional.

**Exemplo de Resposta Padrão de Risco (CVV):**
"Sinto muito que você esteja passando por um momento tão difícil e pensando nisso. É muito importante buscar ajuda profissional agora. Por favor, entre em contato com o CVV (Centro de Valorização da Vida) ligando para o número 188. A ligação é gratuita e eles estão disponíveis 24 horas por dia para conversar com você de forma sigilosa. Você não está sozinho(a) e há pessoas prontas para te ouvir."

Responda sempre de forma concisa e centrada no usuário. Adapte levemente suas respostas para não parecerem repetitivas, mas mantenha a essência empática e segura.
""" # << CERTIFIQUE-SE DE QUE ESTA INSTRUÇÃO ESTÁ COMPLETA E CORRETA

# --- Bloco 6: Definições de Segurança (CVV) ---
keywords_risco = [ "me matar", "me mate", "suicidio", "suicídio", "não aguento mais viver", "quero morrer", "queria morrer", "quero sumir", "desistir de tudo", "acabar com tudo", "fazer mal a mim", "me cortar", "me machucar", "automutilação" ]
resposta_risco_padrao = ( "Sinto muito que você esteja passando por um momento tão difícil e pensando nisso. É muito importante buscar ajuda profissional agora. Por favor, entre em contato com o CVV (Centro de Valorização da Vida) ligando para o número 188. A ligação é gratuita e eles estão disponíveis 24 horas por dia para conversar com você de forma sigilosa. Você não está sozinho(a) e há pessoas prontas para te ouvir." )

# --- Bloco 7: Função para Inicializar o Modelo ---
@st.cache_resource # Guarda o modelo na memória para não recarregar toda hora
def init_model():
    try:
        model = genai.GenerativeModel(
            "gemini-1.5-flash", # Modelo do Gemini
            generation_config=generation_config,
            safety_settings=safety_settings,
            system_instruction=system_instruction # Passa a personalidade aqui
        )
        return model
    except Exception as e:
        st.error(f"Erro grave ao carregar o modelo de IA: {e}")
        st.stop()
model = init_model()

# --- Bloco 8: Gerenciamento do Histórico da Conversa ---
# Cria a memória da conversa se ela não existir
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou Aura. Como você está se sentindo hoje?"}]
# Inicia a sessão de chat com o Gemini se não existir
if "chat_session" not in st.session_state:
     # Não precisa mais passar a system instruction aqui, já foi no init_model
    st.session_state.chat_session = model.start_chat(history=[])

# --- Bloco 9: Exibição do Histórico ---
# Mostra as mensagens antigas na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Bloco 10: Input e Lógica Principal ---
# Caixa para o usuário digitar a mensagem
if prompt := st.chat_input("Digite sua mensagem aqui..."):
    # Adiciona a mensagem do usuário ao histórico e mostra na tela
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Verifica se a mensagem contém palavras de risco
    prompt_lower = prompt.lower() # Converte para minúsculas para facilitar a busca
    contem_risco = any(keyword in prompt_lower for keyword in keywords_risco)

    if contem_risco:
        # Se contém risco, mostra a mensagem do CVV e NÃO envia para a IA
        with st.chat_message("assistant"):
            st.warning("Importante: Se você está pensando em se machucar, por favor, busque ajuda profissional imediatamente.")
            st.markdown(resposta_risco_padrao)
        # Adiciona a resposta de risco ao histórico
        st.session_state.messages.append({"role": "assistant", "content": resposta_risco_padrao})
    else:
        # Se NÃO contém risco, envia para a IA processar
        try:
            with st.spinner("Aura está pensando... 💬"): # Mostra mensagem de "carregando"
                response = st.session_state.chat_session.send_message(prompt)
            bot_response = response.text
            # Adiciona a resposta da IA ao histórico e mostra na tela
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            with st.chat_message("assistant"):
                # Efeito de digitação para a resposta da IA
                message_placeholder = st.empty()
                full_response = ""
                for chunk in bot_response.split():
                    full_response += chunk + " "
                    time.sleep(0.05) # Pequena pausa para simular digitação
                    message_placeholder.markdown(full_response + "▌") # Mostra o cursor piscando
                message_placeholder.markdown(full_response) # Mostra a resposta completa

        except Exception as e:
            # Se der erro ao falar com a IA
            error_msg_user = f"Desculpe, ocorreu um problema técnico ao processar sua mensagem. Tente novamente mais tarde."
            st.error(error_msg_user)
            # Adiciona uma mensagem de erro genérica ao histórico
            error_response = "Sinto muito, tive um problema técnico interno. 😔"
            st.session_state.messages.append({"role": "assistant", "content": error_response})
            print(f"ERRO DEBUG App: Falha Gemini - {e}") # Log técnico (não visível ao usuário)


# --- Bloco 11: Rodapé ---
st.divider()
st.caption("Lembre-se: Aura é uma IA, não um terapeuta. Em caso de emergência ou necessidade de apoio profissional, ligue para o CVV (188) ou procure um profissional de saúde mental.")

# --- Fim do app.py ---