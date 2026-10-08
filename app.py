import streamlit as st
from google import genai
from google.genai import types
from twilio.rest import Client

from prompts import ACTIONLENS_PROMPT


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="ActionLens AI",
    page_icon="👁️",
    layout="wide"
)


# ==========================================
# GEMINI
# ==========================================

gemini_client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

MODEL = "gemini-3.8-flash"


# ==========================================
# TWILIO
# ==========================================

twilio_client = Client(
    st.secrets["TWILIO_ACCOUNT_SID"],
    st.secrets["TWILIO_AUTH_TOKEN"]
)

TWILIO_WHATSAPP_NUMBER = (
    st.secrets["TWILIO_WHATSAPP_NUMBER"]
)


# ==========================================
# SESSION STATE
# ==========================================

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "chat" not in st.session_state:
    st.session_state.chat = None


# ==========================================
# HEADER
# ==========================================

st.title("👁️ ActionLens AI")

st.markdown(
    """
    ### Turn anything you see into something you can act on.

    Upload a notice, document, study material,
    receipt, product or other visual information.
    """
)


# ==========================================
# IMAGE UPLOAD
# ==========================================

uploaded_file = st.file_uploader(
    "📷 Upload an image",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp"
    ]
)


if uploaded_file:

    image_bytes = uploaded_file.getvalue()

    col1, col2 = st.columns(2)


    # ======================================
    # IMAGE
    # ======================================

    with col1:

        st.subheader("📷 Uploaded Image")

        st.image(
            image_bytes,
            width="stretch"
        )


    # ======================================
    # GEMINI ANALYSIS
    # ======================================

    with col2:

        st.subheader("🧠 ActionLens")

        if st.button(
            "🔍 Analyze Image",
            type="primary"
        ):

            with st.spinner(
                "Gemini is understanding your image..."
            ):

                try:

                    response = (
                        gemini_client
                        .models
                        .generate_content(
                            model=MODEL,
                            contents=[
                                types.Part.from_text(
                                    text=ACTIONLENS_PROMPT
                                ),
                                types.Part.from_bytes(
                                    data=image_bytes,
                                    mime_type=uploaded_file.type
                                )
                            ]
                        )
                    )

                    analysis = response.text

                    st.session_state.analysis = (
                        analysis
                    )


                    # ==================================
                    # CREATE GEMINI CHAT
                    # ==================================

                    st.session_state.chat = (
                        gemini_client.chats.create(
                            model=MODEL
                        )
                    )


                    # Give analysis as chat context

                    st.session_state.chat.send_message(
                        f"""
                        The user uploaded an image.

                        Here is the initial ActionLens
                        analysis of that image:

                        {analysis}

                        Use this analysis as context
                        for future questions.

                        Do not invent information that
                        is not supported by the image.
                        """
                    )


                    st.success(
                        "Image analyzed successfully!"
                    )


                except Exception as e:

                    st.error(
                        f"Gemini error: {e}"
                    )


# ==========================================
# DISPLAY ANALYSIS
# ==========================================

if st.session_state.analysis:

    st.divider()

    st.subheader(
        "🎯 ActionLens Analysis"
    )

    st.markdown(
        st.session_state.analysis
    )


    # ======================================
    # WHATSAPP SECTION
    # ======================================

    st.divider()

    st.subheader(
        "📱 Send Analysis to WhatsApp"
    )

    st.write(
        "Get this ActionLens result directly "
        "on your WhatsApp."
    )


    phone_number = st.text_input(
        "WhatsApp number",
        placeholder="+919876543210"
    )


    if st.button(
        "📲 Send to WhatsApp"
    ):

        if not phone_number:

            st.warning(
                "Please enter your WhatsApp number."
            )

        else:

            # Remove accidental spaces

            phone_number = (
                phone_number
                .replace(" ", "")
                .strip()
            )


            # Add whatsapp prefix

            whatsapp_to = (
                f"whatsapp:{phone_number}"
            )


            try:

                message = (
                    twilio_client
                    .messages
                    .create(
                        body=(
                            "👁️ ACTIONLENS AI\n\n"
                            + st.session_state.analysis
                        ),
                        from_=(
                            TWILIO_WHATSAPP_NUMBER
                        ),
                        to=whatsapp_to
                    )
                )


                st.success(
                    "✅ Analysis sent to WhatsApp!"
                )

                st.caption(
                    f"Message ID: {message.sid}"
                )


            except Exception as e:

                st.error(
                    f"Twilio error: {e}"
                )


# ==========================================
# GEMINI CHAT
# ==========================================

if st.session_state.chat:

    st.divider()

    st.subheader(
        "💬 Chat with ActionLens"
    )


    user_question = st.chat_input(
        "Ask something about the image..."
    )


    if user_question:

        st.chat_message(
            "user"
        ).write(
            user_question
        )


        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "ActionLens is thinking..."
            ):

                try:

                    response = (
                        st.session_state.chat
                        .send_message(
                            user_question
                        )
                    )

                    st.write(
                        response.text
                    )

                except Exception as e:

                    st.error(
                        f"Chat error: {e}"
                    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Powered by Gemini Vision • Gemini Chat • Twilio WhatsApp"
)