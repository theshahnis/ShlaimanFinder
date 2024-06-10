from app import create_app, db
from app.models import Show
from datetime import datetime
import pytz

app = create_app()

def populate_shows():
    amsterdam_tz = pytz.timezone('Europe/Amsterdam')
    shows = [
        {
            'name': 'Electric Callboy',
            'start_time': datetime(2024, 6, 27, 23, 15),
            'end_time': datetime(2024, 6, 28, 0, 45),
            'stage': 'Eagle'
        },
        {
            'name': 'Bad Religion',
            'start_time': datetime(2024, 6, 27, 22, 15),
            'end_time': datetime(2024, 6, 27, 23, 15),
            'stage': 'Vulture'
        },
        {
            'name': 'Get The Shot',
            'start_time': datetime(2024, 6, 27, 22, 15),
            'end_time': datetime(2024, 6, 27, 23, 15),
            'stage': 'Buzzard'
        },
        {
            'name': 'Authority Zero',
            'start_time': datetime(2024, 6, 27, 23, 15),
            'end_time': datetime(2024, 6, 28, 0, 0),
            'stage': 'Hawk'
        },
        {
            'name': 'Emo Night Mainland',
            'start_time': datetime(2024, 6, 27, 17, 0),
            'end_time': datetime(2024, 6, 28, 1, 0),
            'stage': 'Raven'
        },
        {
            'name': 'Body Count',
            'start_time': datetime(2024, 6, 27, 21, 0),
            'end_time': datetime(2024, 6, 27, 22, 15),
            'stage': 'Eagle'
        },
        {
            'name': 'Imminence',
            'start_time': datetime(2024, 6, 27, 20, 30),
            'end_time': datetime(2024, 6, 27, 21, 15),
            'stage': 'Eagle'
        },
        {
            'name': 'Body Count ft. Ice-T',
            'start_time': datetime(2024, 6, 27, 21, 15),
            'end_time': datetime(2024, 6, 27, 22, 15),
            'stage': 'Eagle'
        },
        {
            'name': 'Madball',
            'start_time': datetime(2024, 6, 27, 19, 45),
            'end_time': datetime(2024, 6, 27, 20, 30),
            'stage': 'Eagle'
        },
        {
            'name': 'Shadow of Intent',
            'start_time': datetime(2024, 6, 27, 18, 15),
            'end_time': datetime(2024, 6, 27, 19, 0),
            'stage': 'Eagle'
        },
        {
            'name': 'Imminence',
            'start_time': datetime(2024, 6, 27, 20, 30),
            'end_time': datetime(2024, 6, 27, 21, 15),
            'stage': 'Vulture'
        },
        {
            'name': 'Movements',
            'start_time': datetime(2024, 6, 27, 19, 0),
            'end_time': datetime(2024, 6, 27, 19, 45),
            'stage': 'Vulture'
        },
        {
            'name': 'Knosis',
            'start_time': datetime(2024, 6, 27, 17, 30),
            'end_time': datetime(2024, 6, 27, 18, 15),
            'stage': 'Vulture'
        },
        {
            'name': 'Ploegendienst',
            'start_time': datetime(2024, 6, 27, 20, 30),
            'end_time': datetime(2024, 6, 27, 21, 15),
            'stage': 'Buzzard'
        },
        {
            'name': 'Hot Mulligan',
            'start_time': datetime(2024, 6, 27, 19, 0),
            'end_time': datetime(2024, 6, 27, 19, 45),
            'stage': 'Buzzard'
        },
        {
            'name': 'Gel',
            'start_time': datetime(2024, 6, 27, 17, 30),
            'end_time': datetime(2024, 6, 27, 18, 15),
            'stage': 'Buzzard'
        },
        {
            'name': 'Sha La Lees',
            'start_time': datetime(2024, 6, 27, 21, 15),
            'end_time': datetime(2024, 6, 27, 22, 0),
            'stage': 'Hawk'
        },
        {
            'name': 'Death Lens',
            'start_time': datetime(2024, 6, 27, 19, 45),
            'end_time': datetime(2024, 6, 27, 20, 30),
            'stage': 'Hawk'
        },
        {
            'name': 'Pressure Pact',
            'start_time': datetime(2024, 6, 27, 18, 15),
            'end_time': datetime(2024, 6, 27, 19, 0),
            'stage': 'Hawk'
        }

    ]

    for show in shows:
        new_show = Show(
            name=show['name'],
            start_time=show['start_time'],
            end_time=show['end_time'],
            stage=show['stage']
        )
        db.session.add(new_show)

    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the database tables are created
        populate_shows()
        print("Shows populated successfully.")
