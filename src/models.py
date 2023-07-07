class Subject:
    def __init__(self, private_id, public_id, title, description, photo_url):
        self.private_id = private_id
        self.public_id = public_id
        self.title = title
        self.description = description
        self.photo_url = photo_url
    
    def to_dict(self):
        return {
            'private_id': self.private_id,
            'public_id': self.public_id,
            'title': self.title,
            'description': self.description,
            'photo_url': self.photo_url
        }

    @staticmethod
    def from_dict(dict):
        return Subject(
            dict['private_id'],
            dict['public_id'],
            dict['title'],
            dict['description'],
            dict['photo_url']
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

    @staticmethod
    def from_dict(dict):
        return Feedback(
            dict['feedback'],
            dict['feedback_id'],
            dict['timestamp']
        )