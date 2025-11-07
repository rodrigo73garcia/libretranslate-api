from flask import Flask, request, jsonify
import argostranslate.package
import argostranslate.translate
import os

app = Flask(__name__)

def install_models():
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()

    language_pairs = [
        ("en", "zh"), ("en", "es"), ("en", "ar"), ("en", "hi"), ("en", "fr"),
        ("en", "ru"), ("en", "pt"), ("en", "bn"), ("en", "id"), ("en", "ur"),
        ("en", "de"), ("en", "ja"), ("en", "sw"), ("en", "mr"), ("en", "te"),
        ("en", "tr"), ("en", "ta"), ("en", "pa"), ("en", "it"), ("en", "nl"),
        ("en", "ko"), ("en", "pt-pt")  # Inclui português de Portugal
    ]

    for from_code, to_code in language_pairs:
        for pkg in available_packages:
            if pkg.from_code == from_code and pkg.to_code == to_code:
                print(f"Instalando modelo {from_code}->{to_code} ...")
                path = pkg.download()
                argostranslate.package.install_from_path(path)
                print("Modelo instalado com sucesso.")
                break

install_models()

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json(force=True)
    source_lang = data.get("source", "auto")
    target_lang = data.get("target", "pt")
    q = data.get("q", "")

    # Map para normalizar pt-BR e pt-PT
    if target_lang == "pt-BR":
        target_lang = "pt"
    elif target_lang == "pt-PT":
        target_lang = "pt-pt"  # assume o modelo pt-pt foi baixado

    installed_languages = argostranslate.translate.get_installed_languages()
    best_source_lang = installed_languages[0]

    for lang in installed_languages:
        if lang.code == source_lang or lang.code == "en":
            best_source_lang = lang
            break

    best_target_lang = [lang for lang in installed_languages if lang.code == target_lang]
    if not best_target_lang:
        return jsonify({"error": f"Target language '{target_lang}' não encontrado"}), 400
    best_target_lang = best_target_lang[0]

    translation = ""
    try:
        translation = best_source_lang.get_translation(best_target_lang).translate(q)
    except Exception as e:
        print(f"Erro na tradução: {e}")
        translation = q

    return jsonify({"translatedText": translation})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
