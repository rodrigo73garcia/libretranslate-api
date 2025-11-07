import os
from flask import Flask, request, jsonify
import argostranslate.package
import argostranslate.translate

app = Flask(__name__)

def install_models():
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    
    for pkg in available_packages:
        if pkg.from_code == "en" and pkg.to_code == "pt":
            print(f"Instalando modelo {pkg.from_code}->{pkg.to_code} ...")
            path = pkg.download()
            argostranslate.package.install_from_path(path)
            print("Modelo instalado com sucesso.")
            break
    else:
        print("Modelo en=>pt não encontrado nos pacotes disponíveis.")

install_models()

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
        print(f"Erro na tradução: {e}")
        translation = q

    return jsonify({"translatedText": translation})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render geralmente define PORT, coloque fallback (ex: 10000)
    app.run(host="0.0.0.0", port=port, debug=False)

