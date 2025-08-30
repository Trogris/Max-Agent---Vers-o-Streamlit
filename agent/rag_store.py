def add_uploaded_files(self, files):
    total_chunks = 0
    report = []
    for f in files:
        name = getattr(f, "name", "arquivo")
        try:
            # garante que vamos ler do início
            try:
                f.seek(0)
            except Exception:
                pass
            raw = f.read()
            text = self._read_any(name, raw)
            if not text or not text.strip():
                report.append({"name": name, "status": "sem texto (PDF escaneado? ou arquivo vazio)"})
                continue
            chunks = chunk_text(text, self.chunk_size, self.chunk_overlap)
            if not chunks:
                report.append({"name": name, "status": "nenhum chunk gerado"})
                continue
            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [{"source": name, "type": "upload", "chunk_idx": i} for i, _ in enumerate(chunks)]
            self.collection.add(documents=chunks, metadatas=metadatas, ids=ids)
            total_chunks += len(chunks)
            report.append({"name": name, "status": f"{len(chunks)} chunk(s)"})
        except Exception as e:
            report.append({"name": name, "status": f"erro: {e}"})
    return total_chunks, report
