import sys
import atproto_client
from ssky.profile_list import ProfileList
from ssky.ssky_session import expand_actor, ssky_client

def profile(name, **kwargs) -> ProfileList:
    try:
        profile = ssky_client().get_profile(expand_actor(name))
        if profile is None:
            print(f'Profile not found', file=sys.stderr)
            return None
        return ProfileList().append(profile.did)
    except atproto_client.exceptions.AtProtocolError as e:
        if 'response' in dir(e) and e.response is not None:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
        elif str(e) is not None and len(str(e)) > 0:
            print(f'{str(e)}', file=sys.stderr)
        else:
            print(f'{e.__class__.__name__}', file=sys.stderr)
        return None