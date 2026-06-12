import streamlit as st

from services.animal_transform_service import generate_animal_transformation


ANIMALS = [
    "Tiger",
    "Lion",
    "Cat",
    "Wolf",
    "Fox",
    "Leopard",
    "Bear",
    "Panda",
    "Eagle",
    "Owl",
    "Rabbit",
    "Horse",
    "Deer",
    "Monkey",
    "Dog"
]


def render_animal_transform():
    st.subheader("🐯 Animal Face Transformer")

    st.markdown(
        """
        Upload a human face image, select an animal style, and generate
        an AI-powered animal face transformation.
        """
    )

    uploaded_image = st.file_uploader(
        "Upload human face image",
        type=["jpg", "jpeg", "png"],
        key="animal_transform_upload"
    )

    animal = st.selectbox(
        "Select animal style",
        ANIMALS,
        key="animal_transform_style"
    )

    if uploaded_image:
        st.image(
            uploaded_image,
            caption="Uploaded Human Image",
            width=300
        )

    if st.button("Generate Animal Transformation", key="generate_animal_transform"):
        if not uploaded_image:
            st.warning("Please upload a human face image first.")
            return

        try:
            with st.spinner("Generating transformation..."):
                image_bytes = generate_animal_transformation(
                    uploaded_image,
                    animal
                )

            st.success("Transformation generated successfully!")

            st.image(
                image_bytes,
                caption=f"{animal} Transformation",
                use_container_width=True
            )

            st.download_button(
                label="Download Transformed Image",
                data=image_bytes,
                file_name=f"{animal.lower()}_transformation.png",
                mime="image/png"
            )

        except Exception as e:
            st.error("Something went wrong while generating the image.")
            st.exception(e)