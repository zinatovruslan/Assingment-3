Case,Start / End,Expected (from A3 Report),Actual
Touching,660 / 720,Available,Available
Touching before booking,560 / 600,Available,Available
Overlap,630 / 690,Unavailable,Unavailable (Overlaps an existing booking)
Overlap by 1 minute,659 / 700,Unavailable,Unavailable (Overlaps an existing booking)
Blocked,"660 / 720, blocked on",Unavailable,Unavailable (Room is blocked)
Exactly 120 minutes,720 / 840,Available,Available
121 minutes,720 / 841,Unavailable,Unavailable (Duration cannot exceed 120 minutes)
Starts now,540 / 570,Unavailable,Unavailable (Start must be after the current time)
Reversed,720 / 660,Unavailable with message,Unavailable (End must be after start)
End of day,1380 / 1440,Available,Available
Beyond day,1380 / 1441,Unavailable with message,Unavailable (Times must be whole minutes from 0 to 1440)
Between two bookings,700 / 800,Available,Available