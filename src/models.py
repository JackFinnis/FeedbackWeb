class Topic:
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
        return Topic(
            dict['private_id'],
            dict['public_id'],
            dict['title'],
            dict['description'],
        )
    
class Comment:
    def __init__(self, comment, comment_id):
        self.comment = comment
        self.comment_id = comment_id
    
    def to_dict(self):
        return {
            'comment': self.comment,
            'comment_id': self.comment_id
        }

    @staticmethod
    def from_dict(dict):
        return Comment(
            dict['comment'],
            dict['comment_id']
        )