# start q_memorizing

DEFAULT_DICT = {}

for i in range(1, 582):
    DEFAULT_DICT[str(i)] = "NON"

DEFAULT_DICT["النبأ"] = "NON"
DEFAULT_DICT["النازعات"] = "NON"
DEFAULT_DICT["عبس"] = "NON"
DEFAULT_DICT["التكوير"] = "NON"
DEFAULT_DICT["الانفطار"] = "NON"
DEFAULT_DICT["المطففين"] = "NON"
DEFAULT_DICT["الانشقاق"] = "NON"
DEFAULT_DICT["البروج"] = "NON"
DEFAULT_DICT["الطارق"] = "NON"
DEFAULT_DICT["الأعلى"] = "NON"
DEFAULT_DICT["الغاشية"] = "NON"
DEFAULT_DICT["الفجر"] = "NON"
DEFAULT_DICT["البلد"] = "NON"
DEFAULT_DICT["الشمس"] = "NON"
DEFAULT_DICT["الليل"] = "NON"
DEFAULT_DICT["الضحى"] = "NON"
DEFAULT_DICT["الشرح"] = "NON"
DEFAULT_DICT["التين"] = "NON"
DEFAULT_DICT["العلق"] = "NON"
DEFAULT_DICT["القدر"] = "NON"
DEFAULT_DICT["البينة"] = "NON"
DEFAULT_DICT["الزلزلة"] = "NON"
DEFAULT_DICT["العاديات"] = "NON"
DEFAULT_DICT["القارعة"] = "NON"
DEFAULT_DICT["التكاثر"] = "NON"
DEFAULT_DICT["العصر"] = "NON"
DEFAULT_DICT["الهمزة"] = "NON"
DEFAULT_DICT["الفيل"] = "NON"
DEFAULT_DICT["قريش"] = "NON"
DEFAULT_DICT["الماعون"] = "NON"
DEFAULT_DICT["الكوثر"] = "NON"
DEFAULT_DICT["الكافرون"] = "NON"
DEFAULT_DICT["النصر"] = "NON"
DEFAULT_DICT["المسد"] = "NON"
DEFAULT_DICT["الإخلاص"] = "NON"
DEFAULT_DICT["الفلق"] = "NON"
DEFAULT_DICT["الناس"] = "NON"


# end q_memorizing

# start q_test

DEFAULT_DICT_FOR_q_test = {}

for i in range(1, 31):
    DEFAULT_DICT_FOR_q_test["الجزء " + str(i)] = {
        "الحزب "
        + str(2 * i - 1): {
            "الربع 1": "NON",
            "الربع 2": "NON",
            "الربع 3": "NON",
            "الربع 4": "NON",
        },
        "الحزب "
        + str(2 * i): {
            "الربع 1": "NON",
            "الربع 2": "NON",
            "الربع 3": "NON",
            "الربع 4": "NON",
        },
    }
# end q_tests

# start q_awqaf_test

DEFAULT_DICT_FOR_q_awqaf_test = {str(i): "NON" for i in range(1, 31)}

# end q_awqaf_test


DEFAULT_DICT_FOR_PERMISSIONS = {"q_memo": {}, "q_test": {}}

for i in range(1, 31):
    DEFAULT_DICT_FOR_PERMISSIONS["q_memo"][str(i)] = "NON"
    DEFAULT_DICT_FOR_PERMISSIONS["q_test"][str(i)] = "NON"


# default json values
def json_default_value():
    return DEFAULT_DICT


def json_default_value_two():
    return DEFAULT_DICT_FOR_q_test


def json_default_value_three():
    return DEFAULT_DICT_FOR_q_awqaf_test


def json_default_value_four():
    return DEFAULT_DICT_FOR_PERMISSIONS