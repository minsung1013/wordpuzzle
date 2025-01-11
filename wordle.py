import streamlit as st
import pandas as pd
import random

# Load the full word list
word_list_all = pd.read_csv('five_letter_words_all.csv').iloc[:, 0].to_list()
easy_words = pd.read_csv('five_letter_words.csv').iloc[:, 0].to_list()

# Define hard words as those in the all words list but not in easy words list
hard_words = [word for word in word_list_all if word not in easy_words]  # Exclude easy words

# Initialize session state
if 'question' not in st.session_state:
    st.session_state.question = random.choice(easy_words)  # Default to easy difficulty
if 'history' not in st.session_state:
    st.session_state.history = []  # Store guesses and feedback
if 'alphabet_status' not in st.session_state:
    st.session_state.alphabet_status = {chr(i): "unknown" for i in range(97, 123)}  # a-z
if 'hint_letters' not in st.session_state:
    st.session_state.hint_letters = set()  # Track revealed letters for hints
if 'hint_count' not in st.session_state:
    st.session_state.hint_count = 0  # Number of hints used
if 'difficulty' not in st.session_state:
    st.session_state.difficulty = "Easy"  # Default difficulty

# Function to reset the game
def reset_game():
    difficulty = st.session_state.difficulty
    if difficulty == "Easy":
        st.session_state.question = random.choice(easy_words)
    elif difficulty == "Hard":
        st.session_state.question = random.choice(hard_words)
        
    st.session_state.history = []
    st.session_state.alphabet_status = {chr(i): "unknown" for i in range(97, 123)}
    st.session_state.hint_letters = set()
    st.session_state.hint_count = 0

# Function to check the player's answer
def check_answer(question, answer):
    if answer.lower() == '':
        answer = question

    if answer not in word_list_all:
        return 'Invalid answer'
    feedback = []
    for i in range(len(question)):
        if question[i] == answer[i]:
            feedback.append('O')  # Correct letter and position
            st.session_state.alphabet_status[answer[i]] = "correct"
        elif answer[i] in question:
            feedback.append('/')  # Correct letter but wrong position
            if st.session_state.alphabet_status[answer[i]] != "correct":
                st.session_state.alphabet_status[answer[i]] = "partial"
        else:
            feedback.append('X')  # Incorrect letter
            st.session_state.alphabet_status[answer[i]] = "hidden"  # Mark as hidden
    return feedback

# Function to provide a hint
def give_hint():
    max_hints = 3 if st.session_state.difficulty == "Easy" else 5
    if st.session_state.hint_count >= max_hints:
        return None  # Limit reached for hints
    
    remaining_letters = [char for char in st.session_state.question if char not in st.session_state.hint_letters]
    if remaining_letters:
        hint_letter = random.choice(remaining_letters)
        st.session_state.hint_letters.add(hint_letter)
        st.session_state.hint_count += 1
        st.session_state.alphabet_status[hint_letter] = "correct"
        return hint_letter
    return None

# Set the background image
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url('background.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stHorizontalBlock"] {
    display: flex;
    justify-content: center;
    gap: 20px;
}
button {
    margin: 0 10px;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# Streamlit UI
st.title("5-Letter Word Guessing Game")
st.write("Guess the 5-letter word! Enter your guess below:")

# Difficulty selector
difficulty = st.radio("Select Difficulty:", ["Easy", "Hard"])
st.session_state.difficulty = difficulty

# Input for the player's guess
player_guess = st.text_input("Your Guess:", max_chars=5).lower()

# Align buttons horizontally
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("Submit"):
        if player_guess == 'loveu':  # Cheat code to reveal the answer
            st.write(f"The correct word is **{st.session_state.question.upper()}**!")
            st.session_state.history.append(('loveu', ['O', 'O', 'O', 'O', 'O']))
        elif len(player_guess) != 5:
            st.error("Please enter a 5-letter word.")
        else:
            feedback = check_answer(st.session_state.question, player_guess)
            if feedback == 'Invalid answer':
                st.error("Invalid word. Please try again.")
            else:
                # Save the attempt and feedback in history, but don't add 'loveu' to history
                if player_guess != 'loveu':
                    st.session_state.history.append((player_guess, feedback))
                # Display feedback
                st.write(f"Feedback: {' '.join(feedback)}")
                # Check for victory
                if feedback == ['O', 'O', 'O', 'O', 'O']:
                    st.success("Congratulations! You guessed the word!")
                    st.balloons()


with col2:
    if st.button("Hint"):
        hint = give_hint()
        if hint:
            st.info(f"Hint: The word contains the letter **{hint.upper()}**!")
        else:
            st.warning("Hint limit reached. No more hints available!")

with col3:
    if st.button("Reset Game"):
        reset_game()
        st.info("The game has been reset!")

# Display the history
if st.session_state.history:
    st.subheader("Guess History")
    for attempt, feedback in st.session_state.history:
        st.write(f"**{attempt.upper()}**: {' '.join(feedback)}")

# Display the alphabet status
st.subheader("Alphabet Status")
alphabet_display = []
for letter, status in st.session_state.alphabet_status.items():
    if status == "unknown":
        alphabet_display.append(letter)
    elif status == "correct":
        alphabet_display.append(f"**:green[{letter.upper()}]**")
    elif status == "partial":
        alphabet_display.append(f"**:blue[{letter.upper()}]**")

st.markdown(" ".join(alphabet_display), unsafe_allow_html=True)
