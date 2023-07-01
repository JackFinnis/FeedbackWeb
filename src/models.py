class Subject:
    def __init__(self, private_id, public_id, title, description):
        self.private_id = private_id
        self.public_id = public_id
        self.title = title
        self.description = description
    
    def to_dict(self):
        return {
            'private_id': self.private_id,
            'public_id': self.public_id,
            'title': self.title,
            'description': self.description
        }

    @staticmethod
    def from_dict(dict):
        return Subject(
            dict['private_id'],
            dict['public_id'],
            dict['title'],
            dict['description'],
        )
    
class Feedback:
    def __init__(self, feedback, feedback_id):
        self.feedback = feedback
        self.feedback_id = feedback_id
    
    def to_dict(self):
        return {
            'feedback': self.feedback,
            'feedback_id': self.feedback_id
        }

    @staticmethod
    def from_dict(dict):
        return Feedback(
            dict['feedback'],
            dict['feedback_id']
        )