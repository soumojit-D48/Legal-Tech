from celery_app import app


@app.task(bind=True)
def process_contract(self, contract_id: str, file_url: str):
    """
    Main scan pipeline task.
    Orchestrates all pipeline steps for contract analysis.
    """
    raise NotImplementedError("process_contract task not yet implemented")


@app.task(bind=True)
def generate_summary(self, contract_id: str):
    """
    Summary card generation task.
    Triggered after all clauses complete.
    """
    raise NotImplementedError("generate_summary task not yet implemented")


@app.task(bind=True)
def generate_counter_offer(self, clause_id: str):
    """
    Counter-offer generation task.
    Triggered on-demand when user requests counter-offer.
    """
    raise NotImplementedError("generate_counter_offer task not yet implemented")


@app.task(bind=True)
def generate_report(self, contract_id: str):
    """
    PDF report generation task.
    Triggered when user requests PDF export.
    """
    raise NotImplementedError("generate_report task not yet implemented")


@app.task(bind=True)
def embed_contract(self, contract_id: str, contract_text: str):
    """
    Embed contract for Q&A RAG.
    Called at the end of main scan task.
    """
    raise NotImplementedError("embed_contract task not yet implemented")


@app.task(bind=True)
def translate_results(self, contract_id: str, target_language: str):
    """
    Re-translate stored results to new language.
    Triggered when user switches language post-scan.
    """
    raise NotImplementedError("translate_results task not yet implemented")


@app.task(bind=True)
def cleanup_expired_reports(self):
    """
    Periodic task to delete reports past 48hr expiry.
    Runs every hour via Celery Beat.
    """
    raise NotImplementedError("cleanup_expired_reports task not yet implemented")
