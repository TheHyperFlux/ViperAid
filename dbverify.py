from app import app, db, Rescuer, Request
with app.app_context():
    rescuers = Rescuer.query.all()
    for r in rescuers:
        print(r.name, r.phone, r.latitude, r.longitude)
    requests = Request.query.all()
    for r in requests:
        print(r.name, r.phone, r.snake_species, r.location, r.request_type)