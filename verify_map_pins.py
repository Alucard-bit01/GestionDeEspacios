from app import app, db
from model.models import MapPin, User

def verify_pins():
    with app.test_client() as client:
        with app.app_context():
            # Clean up old pins
            MapPin.query.filter_by(name='Test Pin').delete()
            db.session.commit()
            print("[INFO] Cleaned up previous test pins.")

            # Test 1: Unauthorized user adding a pin
            # (Assuming testuser1 exists from previous tests or creating it)
            u = User.query.filter_by(role='user').first()
            if not u:
                print("[WARN] No basic user found for testing, skipping negative test.")
            else:
                client.post('/login', data={'username': u.username, 'password': '123'}, follow_redirects=True)
                res = client.post('/map/pins', json={'name': 'Illegal Pin', 'lat': 0, 'lng': 0})
                if res.status_code == 403:
                    print("[INFO] Correctly blocked basic user from adding pins.")
                else:
                    print(f"[ERROR] Basic user was NOT blocked from adding pins! Status: {res.status_code}")
                client.get('/logout')

            # Test 2: Admin adding a pin
            admin = User.query.filter_by(role='admin').first()
            if not admin:
                print("[ERROR] No admin user found for testing.")
                return

            client.post('/login', data={'username': admin.username, 'password': '123'}, follow_redirects=True)
            res = client.post('/map/pins', json={'name': 'Test Pin', 'lat': 21.1685, 'lng': -100.9317})
            if res.status_code == 200:
                print("[INFO] Admin successfully added a map pin.")
            else:
                print(f"[ERROR] Admin failed to add map pin. Status: {res.status_code}")

            # Test 3: Retrieving pins
            res = client.get('/map/pins')
            print(f"[DEBUG] GET /map/pins status: {res.status_code}")
            print(f"[DEBUG] GET /map/pins data: {res.data}")
            data = res.get_json()
            if data and 'pins' in data and any(p['name'] == 'Test Pin' for p in data['pins']):
                print("[INFO] Pin retrieval verified.")
            else:
                print(f"[ERROR] Added pin not found or bad data: {data}")

            # Final Cleanup
            MapPin.query.filter_by(name='Test Pin').delete()
            db.session.commit()
            print("[INFO] Final cleanup complete.")

if __name__ == '__main__':
    verify_pins()
