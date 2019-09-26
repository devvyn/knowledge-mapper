# %%
"""
fn get list of course details data:
    get list of study_levels
    get list of program_subjects_urls
    for program subject details page in program_subjects_urls:
        get list of program urls
        for program details page in program urls:
            get list of course urls
            for course details page in course urls:
                get course details data
"""

# %%
import subjects

"""
> get list of study_levels
> get list of program_subjects_urls
"""

program_subjects = subjects.fetch_subjects_by_study_level()

