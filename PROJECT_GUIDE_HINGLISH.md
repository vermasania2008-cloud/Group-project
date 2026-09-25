# EduSearch AI - Easy Project Guide (Hinglish)

## 1. Project ka simple idea

EduSearch AI ek student study platform hai. Iska main goal hai ki student ek hi app se:

- question papers analyze kare,
- AI se study doubts puche,
- PDF ke basis par timetable banaye,
- apni daily achievements track kare,
- focus timer use kare,
- purani AI chats dekhe.

App ka main entry point `dash.py` hai.

## 2. App ka complete workflow

1. User `dash.py` se app start karta hai.
2. `auth.py` login/register check karta hai.
3. Login ke baad sidebar mein saare study tools dikhte hain.
4. User kisi page par jaata hai aur input deta hai, jaise PDF, question, time ya achievement.
5. Streamlit page input process karta hai.
6. Result ya to browser/session state mein dikhta hai, ya SQLite/CSV file mein save hota hai.
7. AI waale features ke liye Gemini API key use hoti hai.

## 3. Tech stack

- **Language:** Python
- **UI framework:** Streamlit
- **Data analysis:** Pandas
- **PDF reading:** pypdf
- **AI engine:** Google Gemini API through `google-genai`
- **Database:** SQLite
- **Local file storage:** CSV files
- **Styling:** CSS files aur Streamlit HTML/CSS markup
- **Authentication:** SQLite users table, password hashing aur URL session token
- **Optional presentation:** `python-pptx` se presentation generate karne ka script

Main dependencies `requirements.txt` mein hain:

```text
streamlit
pandas
pypdf
google-genai
python-dotenv
```

## 4. Important files aur unka kaam

| File/folder | Kaam |
|---|---|
| `dash.py` | Main dashboard aur app ka home page |
| `auth.py` | Register, login, logout aur authentication session |
| `pages/que.py` | Question Paper Analyzer |
| `pages/ai.py` | Gemini AI Assistant |
| `pages/timetable.py` | PDF se AI timetable generator |
| `pages/tda.py` | Today's Achievement tracker |
| `pages/timer.py` | Focus/Break study timer |
| `pages/his.py` | AI chat history aur deleted history |
| `style.css` | Common app styling |
| `pages/*.css` | Individual pages ki styling |
| `pages/achievements.csv` | Achievements ka local record |
| `auth.db` | Users aur login sessions; app run hone par ban sakta hai |
| `chat_history.db` | AI chats aur completed focus sessions |
| `.env` | Gemini API key; isse public/share nahi karna |
| `generate_presentation.py` | Project presentation banane ka optional script |

## 5. Features jo abhi kaam kar rahe hain

### Login aur registration

- Naya account username, email aur password se ban sakta hai.
- Username ya email se login ho sakta hai.
- Logout available hai.
- Login ke bina protected pages open nahi hote.
- Login session URL ke `auth_token` ke through restore hota hai.

### Dashboard

Dashboard par user name, analyzed papers, found questions aur detected topics ke metrics dikhte hain. Quick access buttons se Achievement, AI Assistant aur History open hoti hai.

### Question Paper Analyzer

- Multiple PDF upload kar sakte hain.
- PDF ka selectable text `pypdf` se extract hota hai.
- Numbered questions ko regex ke through alag kiya jaata hai.
- Same/repeated questions count kiye jaate hain.
- Paper-wise analysis table dikhti hai.
- Analysis CSV download kar sakte hain.
- Scanned/image-only PDF ke liye OCR abhi available nahi hai.

### AI Assistant

- Normal study question pooch sakte hain.
- PDF/file upload karke uske basis par explanation le sakte hain.
- Gemini academic tutor instructions ke saath answer generate karta hai.
- Chat question aur answer SQLite mein save hote hain.
- Multiple Gemini API keys fallback ke liye support hoti hain, jaise `GEMINI_API_KEY_2`.

### AI Timetable Maker

- Study PDF upload karo.
- Available study time likho, jaise `3 hours tonight`.
- Gemini PDF ke topics ke basis par detailed timetable banata hai.
- Time blocks, breaks, priority, practice aur revision include karne ko prompt diya gaya hai.
- Generated timetable AI History mein save hota hai.

### Today's Achievement

- Daily achievement add kar sakte hain.
- Category aur status select kar sakte hain.
- Completed, In Progress aur Planned count dikhte hain.
- Daily progress percentage calculate hota hai.
- Data `pages/achievements.csv` mein save hota hai.
- Aaj ke achievements delete kar sakte hain.

### Study Timer

- Focus aur Break mode hai.
- Default focus 25 minutes aur break 5 minutes hai.
- Focus aur break duration change ki ja sakti hai.
- Timer pause, resume aur reset support karta hai.
- Completed focus session ka task, duration, date aur time SQLite mein save hota hai.
- Aaj ka total focus time aur sessions dikhte hain.

### History

- Sirf current logged-in user ki chats dikhai jaati hain.
- Question text se search kar sakte hain.
- Chat open karke full answer dekh sakte hain.
- Chat ko Deleted History mein move kar sakte hain.
- Deleted history ko empty karne ka option bhi hai.

## 6. App ko run kaise karein

Project folder mein PowerShell/Terminal open karke:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run dash.py
```

Browser mein normally ye URL open hoga:

```text
http://localhost:8501
```

AI features ke liye project ke root `.env` file mein key add karein:

```text
GEMINI_API_KEY=your_api_key_here
```

API key ko GitHub ya kisi public place par upload nahi karna chahiye.

## 7. Current limitations / almost features

- **Topics Detected:** Dashboard mein value currently `0` set hoti hai; real topic extraction abhi implement nahi hai.
- **Streak:** Dashboard par abhi real streak calculation nahi, sirf `Ready` text hai.
- **Achievement AI insight:** Text fixed rule-based message hai; actual Gemini analysis nahi ho raha.
- **Question matching:** Repetition mostly exact normalized text par based hai. Same meaning wale thode different questions automatically merge nahi honge.
- **Scanned PDFs:** OCR nahi hai, isliye image-only PDFs analyze nahi honge.
- **AI dependency:** Gemini API key, internet aur valid model/API access ke bina AI Assistant aur Timetable Maker nahi chalenge.
- **Presentation script:** `generate_presentation.py` optional hai; iske liye `python-pptx` ko requirements mein alag se add/install karna pad sakta hai.
- **Security improvement:** Password SHA-256 se hash ho raha hai, lekin production app ke liye salted password hashing library, jaise Argon2/bcrypt, better rahegi.

## 8. User ke liye best usage flow

1. Account create karke login karo.
2. Purane question papers `Question Paper Analyzer` mein upload karo.
3. Repeated questions aur CSV result se important topics identify karo.
4. Study PDF ke liye `Timetable Maker` se plan banao.
5. Doubts ke liye `AI Assistant` use karo.
6. Focus sessions `Study Timer` se complete karo.
7. Daily progress `Today's Achievement` mein record karo.
8. Purani AI help `History` page se revise karo.

## 9. One-line project summary

**EduSearch AI ek Streamlit-based smart study workspace hai jo PDF analysis, Gemini tutoring, timetable planning, focus tracking aur achievement management ko ek app mein combine karta hai.**
