import streamlit as st
import json
import os
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

# ---------- Setup ----------
st.set_page_config(page_title="📚 Advanced Library Manager", layout="wide")
DATA_FILE = "library.json"
COVER_FOLDER = "covers"

os.makedirs(COVER_FOLDER, exist_ok=True)

# ---------- Load/Save ----------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

if 'library' not in st.session_state:
    st.session_state.library = load_data()

library = st.session_state.library

# ---------- Sidebar Menu ----------
st.sidebar.title("📖 Menu")
menu = st.sidebar.radio("Select Option", [
    "Add Book", "View Library", "Search Books", 
    "Statistics", "Recommendations", "Export Library"
])

dark_mode = st.sidebar.checkbox("🌙 Dark Mode")
if dark_mode:
    st.markdown("<style>.stApp {background-color: #1e1e1e;  color: white;}</style>", unsafe_allow_html=True)

# ---------- Add Book ----------
if menu == "Add Book":
    st.title("➕ Add New Book")
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    year = st.number_input("Publication Year", min_value=1000, max_value=2100)
    genre = st.text_input("Genre")
    read = st.radio("Read?", ["Yes", "No"])
    rating = st.slider("Rate this Book (1-5)", 1, 5, 3)
    cover_image = st.file_uploader("Upload Book Cover (optional)", type=["jpg", "jpeg", "png"])

    if st.button("Add Book"):
        if title and author and genre:
            cover_path = ""
            if cover_image:
                cover_path = os.path.join(COVER_FOLDER, cover_image.name)
                with open(cover_path, "wb") as f:
                    f.write(cover_image.read())

            new_book = {
                "title": title,
                "author": author,
                "year": int(year),
                "genre": genre,
                "read": read == "Yes",
                "rating": rating,
                "cover": cover_path
            }
            library.append(new_book)
            save_data(library)
            st.success("📗 Book added!")
        else:
            st.warning("Please fill all required fields.")

# ---------- View All ----------
elif menu == "View Library":
    st.title("📚 Your Library")

    if library:
        for i, book in enumerate(library):
            with st.expander(f"{i+1}. {book['title']}"):
                cols = st.columns([1, 3])
                with cols[0]:
                    if book["cover"] and os.path.exists(book["cover"]):
                        st.image(book["cover"], width=100)
                    else:
                        st.write("📕 No cover")
                with cols[1]:
                    st.markdown(f"""
                    **Title:** {book['title']}  
                    **Author:** {book['author']}  
                    **Year:** {book['year']}  
                    **Genre:** {book['genre']}  
                    **Read:** {"✅" if book['read'] else "❌"}  
                    **Rating:** {'⭐' * book['rating']}
                    """)

                    # Edit
                    if st.button("✏️ Edit", key=f"edit_{i}"):
                        with st.form(f"edit_form_{i}"):
                            new_title = st.text_input("Title", book['title'])
                            new_author = st.text_input("Author", book['author'])
                            new_year = st.number_input("Year", value=book['year'])
                            new_genre = st.text_input("Genre", book['genre'])
                            new_read = st.radio("Read?", ["Yes", "No"], index=0 if book['read'] else 1)
                            new_rating = st.slider("Rating", 1, 5, book['rating'])
                            submitted = st.form_submit_button("Save Changes")
                            if submitted:
                                book.update({
                                    "title": new_title,
                                    "author": new_author,
                                    "year": int(new_year),
                                    "genre": new_genre,
                                    "read": new_read == "Yes",
                                    "rating": new_rating
                                })
                                save_data(library)
                                st.success("✅ Updated!")
                                st.experimental_rerun()

                    if st.button("🗑️ Delete", key=f"delete_{i}"):
                        library.pop(i)
                        save_data(library)
                        st.warning("Book deleted!")
                        st.experimental_rerun()
    else:
        st.info("No books yet. Add some!")

# ---------- Search ----------
elif menu == "Search Books":
    st.title("🔍 Search Your Library")
    query = st.text_input("Search by Title or Author")

    if query:
        results = [b for b in library if query.lower() in b['title'].lower() or query.lower() in b['author'].lower()]
        if results:
            for book in results:
                st.markdown(f"📘 **{book['title']}** by *{book['author']}* - {'✅ Read' if book['read'] else '❌ Unread'}")
        else:
            st.warning("No matches found.")

# ---------- Statistics ----------
elif menu == "Statistics":
    st.title("📊 Library Statistics")
    total = len(library)
    read = sum(1 for b in library if b['read'])
    unread = total - read
    genres = pd.Series([b['genre'] for b in library])

    st.metric("Total Books", total)
    st.metric("Books Read", read)
    st.metric("Unread", unread)

    # Pie Chart
    st.markdown("### Read vs Unread")
    fig1, ax1 = plt.subplots()
    ax1.pie([read, unread], labels=["Read", "Unread"], autopct='%1.1f%%', colors=["green", "red"])
    st.pyplot(fig1)

    st.markdown("### Genre Distribution")
    fig2, ax2 = plt.subplots()
    genres.value_counts().plot(kind="bar", color="skyblue", ax=ax2)
    st.pyplot(fig2)

# ---------- Recommendations ----------
elif menu == "Recommendations":
    st.title("🎯 Smart Recommendations")
    most_read_genre = pd.Series([b['genre'] for b in library if b['read']]).mode()
    top_rated = sorted([b for b in library if b['rating'] >= 4], key=lambda x: x['rating'], reverse=True)

    if most_read_genre.any():
        st.subheader(f"📘 Based on your favorite genre: *{most_read_genre[0]}*")
        for book in library:
            if book['genre'] == most_read_genre[0]:
                st.markdown(f"**{book['title']}** by *{book['author']}*")

    st.subheader("⭐ Top Rated Books")
    for book in top_rated[:3]:
        st.markdown(f"{'⭐' * book['rating']} **{book['title']}** by *{book['author']}*")

# ---------- Export ----------
elif menu == "Export Library":
    st.title("📤 Export Your Library")
    if library:
        df = pd.DataFrame(library)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download as CSV", csv, "library.csv", "text/csv")
    else:
        st.info("Nothing to export.")

