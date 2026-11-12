from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "model_final_fraudex.pkl"

_data = joblib.load(MODEL_PATH)
_pipe = _data["model"]
BATAS_BERBAHAYA = _data["threshold_penipuan"]
BATAS_WASPADA = _data["threshold_waspada"]

_tfidf = _pipe.named_steps["tfidf"]
_lr = _pipe.named_steps["lr"]
_vocab = _tfidf.get_feature_names_out()

KELAS_PENIPUAN = 1
_idx = list(_lr.classes_).index(KELAS_PENIPUAN)
_coef = _lr.coef_[0] if _idx == 1 else -_lr.coef_[0]

# <-- STOPWORD ditaruh di sini
STOPWORD = {"ini", "itu", "ke", "di", "yang", "dan", "untuk", "anda", "saya", "kamu",
            "dari", "dengan", "pada", "atau", "ya", "nanti", "dulu", "tolong"}


def analisis(teks: str, top_k: int = 5) -> dict:
    skor = float(_pipe.predict_proba([teks])[0][_idx])

    if skor >= BATAS_BERBAHAYA:
        risiko = "berbahaya"
    elif skor >= BATAS_WASPADA:
        risiko = "waspada"
    else:
        risiko = "aman"

    X = _tfidf.transform([teks]).tocoo()
    kontribusi = [
        (_vocab[c], v * _coef[c])
        for c, v in zip(X.col, X.data)
        if v * _coef[c] > 0
        and not _vocab[c].isdigit()
        and len(_vocab[c]) > 2
        and _vocab[c] not in STOPWORD
    ]
    kontribusi.sort(key=lambda x: x[1], reverse=True)
    kata = [k for k, _ in kontribusi[:top_k]]

    if risiko == "aman":
        kata = []

    return {
        "tingkat_risiko": risiko,
        "skor_kepercayaan": round(skor, 4),
        "kata_highlight": kata,
    }