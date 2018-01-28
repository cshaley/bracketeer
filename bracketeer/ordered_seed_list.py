from collections import OrderedDict

num_slots = 135
num_seeds = 72
seedlist = [
    'W11a', 'W11b', 'W16a', 'W16b',
    'Y16a', 'Y16b', 'Z11a', 'Z11b',
    'W01', 'W16', 'W08', 'W09',
    'W05', 'W12', 'W04', 'W13',
    'W06', 'W11', 'W03', 'W14',
    'W07', 'W10', 'W02', 'W15',
    'X01', 'X16', 'X08', 'X09',
    'X05', 'X12', 'X04', 'X13',
    'X06', 'X11', 'X03', 'X14',
    'X07', 'X10', 'X02', 'X15',
    'Y01', 'Y16', 'Y08', 'Y09',
    'Y05', 'Y12', 'Y04', 'Y13',
    'Y06', 'Y11', 'Y03', 'Y14',
    'Y07', 'Y10', 'Y02', 'Y15',
    'Z01', 'Z16', 'Z08', 'Z09',
    'Z05', 'Z12', 'Z04', 'Z13',
    'Z06', 'Z11', 'Z03', 'Z14',
    'Z07', 'Z10', 'Z02', 'Z15',
]
seed_slot_map = OrderedDict(
    zip(range(1, num_slots + 1), seedlist + list(range(num_slots - num_seeds)))
)

