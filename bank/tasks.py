from models import db, CreditApplication

def process_credit_application(application_id):
    # пример: изменить статус заявки на "Обработано"
    application = CreditApplication.query.get(application_id)
    if application:
        application.status = "Обработано"
        db.session.commit()