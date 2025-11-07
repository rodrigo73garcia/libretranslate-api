from flask import Flask, request, jsonify
import argostranslate.package
import argostranslate.translate
import os

app = Flask(__name__)

def download_and_install_models():
    if not os.path.exists("en_pt.argosmodel"):
        os.system("wget https://github.com/argosopentech/argos-translate/releases/download/v1.0/en_pt.argosmodel")
    argostranslate.package.install_from_path("en_pt.argosmodel")

download_and_install_models()

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json(force=True)
    source_lang = data.get("source", "auto")
    target_lang = data.get("target", "pt")
    q = data.get("q", "")

    installed_languages = argostranslate.translate.get_installed_languages()
    best_source_lang = installed_languages[0]

    for lang in installed_languages:
        if lang.code == source_lang or lang.code == "en":
            best_source_lang = lang
            break

    best_target_lang = [lang for lang in installed_languages if lang.code == target_lang]
    if not best_target_lang:
        return jsonify({"error": f"Target language '{target_lang}' not found"}), 400
    best_target_lang = best_target_lang[0]

    translation = ""
    try:
        translation = best_source_lang.get_translation(best_target_lang).translate(q)
    except Exception as e:
        translation = q

    return jsonify({"translatedText": translation})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
