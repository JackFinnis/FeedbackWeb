import datetime

class Subject:
    def __init__(self, private_id, public_id, title, description, photo_url, live, shown_save_alert):
        self.private_id = private_id
        self.public_id = public_id
        self.title = title
        self.description = description
        self.photo_url = photo_url
        self.live = live
        self.shown_save_alert = shown_save_alert
    
    def to_dict(self):
        return {
            'private_id': self.private_id,
            'public_id': self.public_id,
            'title': self.title,
            'description': self.description,
            'photo_url': self.photo_url,
            'live': self.live,
            'shown_save_alert': self.shown_save_alert,
        }

    @staticmethod
    def from_dict(dict):
        return Subject(
            dict['private_id'],
            dict['public_id'],
            dict['title'],
            dict['description'],
            dict['photo_url'],
            dict['live'],
            dict['shown_save_alert']
        )
    
class Feedback:
    def __init__(self, feedback, feedback_id, timestamp):
        self.feedback = feedback
        self.feedback_id = feedback_id
        self.timestamp = timestamp
    
    def to_dict(self):
        return {
            'feedback': self.feedback,
            'feedback_id': self.feedback_id,
            'timestamp': self.timestamp
        }
    
    def get_formatted_timestamp(self):
        return format_date(self.timestamp)

    @staticmethod
    def from_dict(dict):
        return Feedback(
            dict['feedback'],
            dict['feedback_id'],
            dict['timestamp']
        )

def format_date(timestamp: datetime.datetime):
    date = timestamp.date()
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    week_ago = today - datetime.timedelta(days=7)
    
    if date == today:
        return timestamp.strftime('%H:%M')
    elif date == yesterday:
        return 'Yesterday'
    elif date >= week_ago:
        return timestamp.strftime('%A')
    elif date.year == today.year:
        return timestamp.strftime('%d %b')
    else:
        return timestamp.strftime('%d %b %Y')