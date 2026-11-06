Baseline Notes
So basically, the booking rules are pretty straightforward:

Time has to be in whole minutes from 0 to 1440.

The start time must be strictly after now.

Max duration is 120 minutes.

If intervals just touch each other, booking is allowed.

If there's even a 1-minute overlap or the room is blocked, you can't book it.

If the end time is before the start or goes past 24 hours, it throws an error message.

As for what's wrong with booking.py when we scale to multiple rooms:

The can_book function is hardcoded for just one room right now.

There's no list or dictionary to keep track of multiple rooms.

The check logic doesn't know anything about room IDs, capacity, or statuses.

What tests we need:

Start equals now → unavailable

Exactly 120 mins → available

121 mins → unavailable

Touching intervals → available

1-minute overlap → unavailable

Room blocked → unavailable

End before start → error

Time over 1440 → error