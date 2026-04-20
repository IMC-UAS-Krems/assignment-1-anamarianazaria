"""
users.py
--------
Implement the class hierarchy for platform users.

Classes to implement:
  - User (base class)
    - FreeUser
    - PremiumUser
    - FamilyAccountUser
    - FamilyMember
"""

class User:
    def __init__(self, user_id, name, age, sessions = None):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.sessions = sessions if sessions is not None else []

    def add_session(self, session):
        self.sessions.append(session)

    def total_listening_seconds(self):
        return sum(session.duration_listened_seconds for session in self.sessions)
    
    def total_listening_minutes(self):
        return self.total_listening_seconds() / 60
    
    def unique_tracks_listened(self):
        return set(
            s.track.track_id
            for s in self.sessions
            if s.track is not None
        )


class FreeUser(User):
    MAX_SKIPS_PER_HOUR = 6

class PremiumUser(User):
    def __init__(self, user_id, name, age, subscription_start, sessions = None):
        super().__init__(user_id, name, age, sessions)
        self.subscription_start = subscription_start

class FamilyAccountUser(User):
    def __init__(self, user_id, name, age, sub_users = None, sessions = None):
        super().__init__(user_id, name, age, sessions)
        self.sub_users = sub_users if sub_users is not None else []

    def add_sub_user(self, sub_user):
        if sub_user not in self.sub_users:
            self.sub_users.append(sub_user)
            sub_user.parent = self
            
    def all_members(self):
        return [self] + self.sub_users
    

class FamilyMember(User):
    def __init__(self, user_id, name, age, parent, sessions = None):
        super().__init__(user_id, name, age, sessions)
        self.parent = parent
