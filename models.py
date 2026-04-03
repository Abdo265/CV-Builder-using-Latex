import re
from typing import List


# ------------------ Common LaTeX Escaper ------------------
def escape_latex(text: str) -> str:
    """
    Escape special LaTeX characters except inside URLs.
    """
    if not text:
        return ""

    # Protect URLs from escaping
    url_pattern = r"(https?://[^\s]+)"
    urls = re.findall(url_pattern, text)

    # Replace each URL with a placeholder
    placeholders = [f"__URL{i}__" for i in range(len(urls))]
    for ph, url in zip(placeholders, urls):
        text = text.replace(url, ph)

    # Escape special LaTeX characters
    text = re.sub(r'([&%$#_{}~^\\])', r'\\\1', text)

    # Replace placeholders back with original URLs (unescaped)
    for ph, url in zip(placeholders, urls):
        text = text.replace(ph, url)

    return text


# ------------------ Certificate ------------------
class Certificate:
    def __init__(self, title, desc, date, verify):
        self.title = escape_latex(title).strip()
        self.desc = escape_latex(desc).strip()
        self.date = escape_latex(date).strip()
        self.verify = verify  # links are not escaped

    @classmethod
    def from_json(cls, data):
        return cls(
            title=data.get("title"),
            desc=data.get("desc"),
            date=data.get("date"),
            verify=data.get("verify")
        )


# ------------------ Course ------------------
class Course:
    def __init__(self, title, desc, location, date, skip):
        self.title = escape_latex(title).strip()
        self.desc = escape_latex(desc).strip()
        self.location = escape_latex(location).strip()
        self.date = escape_latex(date).strip()
        self.skip = skip

    @classmethod
    def from_json(cls, data):
        return cls(
            title=data.get("title"),
            desc=data.get("desc"),
            location=data.get("location"),
            date=data.get("date"),
            skip=data.get("skip", False)
        )


# ------------------ Education ------------------
class Education:
    def __init__(self, title, desc, materials, date, location):
        self.title = escape_latex(title).strip()
        self.desc = escape_latex(desc).strip()
        self.materials = escape_latex(materials).strip()
        self.date = escape_latex(date).strip()
        self.location = escape_latex(location).strip()

    @classmethod
    def from_json(cls, data):
        return cls(
            title=data.get("title"),
            desc=data.get("desc"),
            materials=data.get("materials"),
            date=data.get("date"),
            location=data.get("location")
        )


# ------------------ Experience ------------------
class Experience:
    def __init__(self, title, desc, date, location):
        self.title = escape_latex(title).strip()
        self.desc = escape_latex(desc).strip()
        self.date = escape_latex(date).strip()
        self.location = escape_latex(location).strip()

    @classmethod
    def from_json(cls, data):
        return cls(
            title=data.get("title"),
            desc=data.get("desc"),
            date=data.get("date"),
            location=data.get("location")
        )


# ------------------ Personal Info ------------------
class PersonalInfo:
    def __init__(self, name, email, phone, location, linkedin, github, portfolio, kaggle):
        self.name = escape_latex(name).strip()
        self.email = escape_latex(email).strip()
        self.phone = escape_latex(phone).strip()
        self.location = escape_latex(location).strip()
        self.linkedin = linkedin
        self.github = github
        self.portfolio = portfolio
        self.kaggle = kaggle

    @classmethod
    def from_json(cls, data):
        return cls(
            name=data.get("name"),
            email=data.get("email"),
            phone=data.get("phone"),
            location=data.get("location"),
            linkedin=data.get("linkedin"),
            github=data.get("github"),
            portfolio=data.get("portfolio"),
            kaggle=data.get("kaggle")
        )


# ------------------ Language ------------------
class Language:
    def __init__(self, language, level):
        self.language = escape_latex(language).strip()
        self.level = escape_latex(level).strip()

    @classmethod
    def from_json(cls, data):
        return cls(
            language=data.get("language"),
            level=data.get("level")
        )


# ------------------ Project ------------------
class Project:
    def __init__(self, title, desc, urls, skip):
        self.title = escape_latex(title).strip()
        self.desc = escape_latex(desc).strip()
        self.urls = urls  # links are not escaped
        self.skip = skip

    @classmethod
    def from_json(cls, data):
        return cls(
            title=data.get("title"),
            desc=data.get("desc"),
            urls=data.get("urls"),
            skip=data.get("skip", False)
        )


# ------------------ Additional Experience ---------
class AdditionalExperience:
    def __init__(
            self,
            title, desc):
        self.title = escape_latex(title).strip()
        self.desc = escape_latex(desc).strip()

    @classmethod
    def from_json(cls, data):
        return cls(
            title=data.get("title"),
            desc=data.get("desc")
        )


# ------------------ Volunteer ------------------
class Volunteer:
    def __init__(self, title, desc, date, urls):
        self.title = escape_latex(title).strip()
        self.desc = escape_latex(desc).strip()
        self.date = escape_latex(date).strip()
        self.urls = urls

    @classmethod
    def from_json(cls, data):
        return cls(
            title=data.get("title"),
            desc=data.get("desc"),
            date=data.get("date"),
            urls=data.get("urls")
        )


# ------------------ PageOptions ------------------
class PageOptions:
    def __init__(self, items_spacing, top_margin, bottom_margin, right_margin, left_margin,
                 section_pre_space, section_post_space, title_font_size, font_size, line_spacing):
        self.items_spacing = items_spacing
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.right_margin = right_margin
        self.left_margin = left_margin
        self.section_pre_space = section_pre_space
        self.section_post_space = section_post_space
        self.title_font_size = title_font_size
        self.font_size = font_size
        self.line_spacing = line_spacing

    @classmethod
    def from_json(cls, data):
        return PageOptions(
            items_spacing=data.get("items_spacing"),
            top_margin=data.get("top_margin"),
            bottom_margin=data.get("bottom_margin"),
            right_margin=data.get("right_margin"),
            left_margin=data.get("left_margin"),
            section_pre_space=data.get("section_pre_space"),
            section_post_space=data.get("section_post_space"),
            title_font_size=data.get("title_font_size"),
            font_size=data.get("font_size"),
            line_spacing=data.get("line_spacing"),
        )


# ------------------ Tech Skills ------------------
class TechSkillTopic:
    def __init__(self, title, values):
        self.title = escape_latex(title).strip()
        self.values = [escape_latex(x).strip() for x in values]

    @classmethod
    def from_json(cls, data):
        return cls(
            title=data.get("title"),
            values=data.get("values"),
        )


# ------------------ Grad Proj ------------------
class GradProj:
    def __init__(self, show, title, desc, technologies, urls):
        self.show = show
        self.title = escape_latex(title).strip()
        self.desc = escape_latex(desc).strip()
        self.technologies = [escape_latex(x) for x in technologies]
        self.urls = urls

    @classmethod
    def from_json(cls, data):
        return cls(
            show=data.get("show"),
            title=data.get("title"),
            desc=data.get("desc"),
            technologies=data.get("technologies"),
            urls=data.get("urls")
        )


# ------------------ CV ------------------
class CV:
    def __init__(
            self,
            personal_info: PersonalInfo,
            career_subject: str,
            education: Education,
            experiences: List[Experience],
            courses: List[Course],
            projects: List[Project],
            volunteers: List[Volunteer],
            tech_skills: List[TechSkillTopic],
            soft_skills: List[str],
            certificates: List[Certificate],
            langs: List[Language],
            additional_experience: List[AdditionalExperience],
            page_options: PageOptions,
            grad_proj: GradProj,
    ):
        self.personal_info = personal_info
        self.career_subject = escape_latex(career_subject).strip()
        self.education = education
        self.experiences = experiences
        self.courses = list(filter(lambda x: not x.skip, courses))
        self.projects = list(filter(lambda x: not x.skip, projects))
        self.volunteers = volunteers
        self.tech_skills = tech_skills
        self.soft_skills = [escape_latex(skill).strip() for skill in soft_skills]
        self.certificates = certificates
        self.langs = langs
        self.additional_experience = additional_experience
        self.page_options = page_options
        self.grad_proj = grad_proj
