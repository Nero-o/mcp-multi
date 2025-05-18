def valida_arquivos(files):
    if len(files) > 10:
        return False, "Máximo de 10 arquivos por envio.", "error"

    for file in files:
        if file.content_length > 15 * 1024 * 1024:
            return False, "Cada arquivo deve ter no máximo 15MB.", "error"

        if not file.filename.endswith(".csv"):
            return False, "Somente arquivos do tipo CSV são permitidos.", "error"

    return (True,"Todos arquivos válidos.", "success")