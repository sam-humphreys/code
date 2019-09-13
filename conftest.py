import hypothesis

# https://hypothesis.readthedocs.io/en/latest/settings.html#settings-profiles
# https://hypothesis.readthedocs.io/en/latest/settings.html#available-settings
hypothesis.settings.register_profile(
    'fast',
    deadline=1000,
    max_examples=25,
)

hypothesis.settings.register_profile(
    'intensive',
    deadline=1500,
    max_examples=100,
)
