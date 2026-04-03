from models import CV

from pylatex import (
    Document, Section, Itemize, Command, NoEscape, Tabularx, Center
)
from pylatex.package import Package

COMMON_ITEMS_MINUS_SPACE = None


def build_cv(cv: CV):
    # Global
    global COMMON_ITEMS_MINUS_SPACE
    COMMON_ITEMS_MINUS_SPACE = rf"\vspace{{{cv.page_options.items_spacing}pt}}"

    doc = _create_doc(cv)
    _build_header(doc, cv)
    _build_career_subject(doc, cv)
    _build_education(doc, cv)
    _build_grad_proj(doc, cv)
    _build_experience(doc, cv)
    _build_course(doc, cv)
    _build_project(doc, cv)
    _build_volunteering(doc, cv)
    _build_tech_skills(doc, cv)
    _build_soft_skills(doc, cv)
    _build_certification(doc, cv)
    _build_additional_experience(doc, cv)
    _build_languages(doc, cv)
    return doc


def _create_doc(cv: CV) -> Document:
    geometry_options = {
        "left": f"{cv.page_options.left_margin}pt",
        "right": f"{cv.page_options.right_margin}pt",
        "top": f"{cv.page_options.top_margin}pt",
        "bottom": f"{cv.page_options.bottom_margin}pt",
    }

    doc = Document(
        documentclass="article",
        document_options=["a4paper", "10pt"],
        geometry_options=geometry_options,
    )

    # ================= Packages =================
    for pkg in [
        "latexsym",
        "titlesec",
        "marvosym",
        "verbatim",
        "enumitem",
        "fancyhdr",
        "tabularx",
        "fontawesome5",
        "multicol",
        "ragged2e",
    ]:
        doc.packages.append(Package(pkg))

    # Load packages that require options ONLY ONCE
    doc.preamble.append(NoEscape(r"\usepackage[hidelinks]{hyperref}"))
    doc.preamble.append(NoEscape(r"\usepackage[usenames,dvipsnames]{xcolor}"))

    doc.preamble.append(NoEscape(r"\setlength{\multicolsep}{-3.0pt}"))
    doc.preamble.append(NoEscape(r"\setlength{\columnsep}{-1pt}"))

    # ================= Header / Footer =================
    doc.preamble.append(NoEscape(r"\pagestyle{fancy}"))
    doc.preamble.append(NoEscape(r"\fancyhf{}"))
    doc.preamble.append(NoEscape(r"\renewcommand{\headrulewidth}{0pt}"))
    doc.preamble.append(NoEscape(r"\renewcommand{\footrulewidth}{0pt}"))

    # ================= Section style =================
    pre_space = cv.page_options.section_pre_space
    post_space = cv.page_options.section_post_space

    doc.preamble.append(NoEscape(rf"""
    \titleformat{{\section}}{{%
      \vspace{{{pre_space}pt}}\scshape\raggedright\bfseries
    }}{{}}{{0em}}{{}}[\color{{black}}\titlerule \vspace{{{post_space}pt}}]
    """))

    font_size = cv.page_options.font_size
    line_spacing = cv.page_options.line_spacing

    doc.preamble.append(NoEscape(rf"""
    \makeatletter
    \renewcommand{{\normalsize}}{{%
       \@setfontsize\normalsize{{{font_size}}}{{{line_spacing}}}%
    }}
    \makeatother
    """))

    return doc


def _build_header(doc: Document, cv: CV):
    info = cv.personal_info

    with doc.create(Center()):
        # Name
        title_font_size = cv.page_options.title_font_size
        line_spacing = cv.page_options.line_spacing

        doc.append(NoEscape(
            rf"{{\fontsize{{{title_font_size}}}{{{line_spacing}}}\selectfont \textbf{{{info.name}}}}} \\"
        ))

        url_to_whatsapp = f"https://wa.me/{cv.personal_info.phone}"

        # Contact info
        links = []
        links.append(rf"\href{{mailto:{cv.personal_info.email}}}{{\faEnvelope\ {cv.personal_info.email}}}")
        links.append(rf"\href{{{url_to_whatsapp}}}{{\faPhone\ {cv.personal_info.phone}}}")
        links.append(rf"\faMapMarker\ {cv.personal_info.location} ~ ")
        links.append(rf"\href{{{cv.personal_info.linkedin}}}{{\faLinkedin\ LinkedIn}} ~ ")
        links.append(rf"\href{{{cv.personal_info.github}}}{{\faGithub\ GitHub}} ~ ")
        if cv.personal_info.portfolio:
            links.append(rf"\href{{{cv.personal_info.portfolio}}}{{\faGlobe\ Portfolio}} ~ ")

        if cv.personal_info.kaggle:
            links.append(rf"\href{{{cv.personal_info.kaggle}}}{{\textbf{{K}} Kaggle}}")

        links_concat = " ~ ".join(links)
        doc.append(NoEscape(
            links_concat
        ))


def _build_career_subject(doc: Document, cv: CV):
    with doc.create(Section("Career Objective")):
        doc.append(NoEscape(r"""
\noindent
\hyphenpenalty=10000
\exhyphenpenalty=10000
{career_subject}
    """.format(career_subject=cv.career_subject)))


def _build_education(doc: Document, cv: CV):
    with doc.create(Section("Education")):
        edu = cv.education  # Your Education object
        materials = edu.materials

        with doc.create(Itemize(options=NoEscape("leftmargin=0.0in, label={}"))):
            doc.append(NoEscape(rf"""
            \item
            \begin{{tabularx}}{{\textwidth}}{{Xr}}
            \textbf{{{edu.title}}} & \textbf{{{edu.date}}} \\
            {edu.desc} & {edu.location} \\
            \textbf{{Materials}}: {edu.materials}
            \end{{tabularx}}
            """))
            doc.append(NoEscape(COMMON_ITEMS_MINUS_SPACE))


def _build_grad_proj(doc: Document, cv: CV):
    if not cv.grad_proj.show:
        return

    with doc.create(Section("Graduation Project")):
        grad = cv.grad_proj

        tech_str = ", ~ ".join(grad.technologies) + r". \\"
        links = " ~ ".join(
            rf"\href{{{url[1]}}}{{\underline{{\textbf{{\textit{{{url[0]}}}}}}}}}" for url in grad.urls
        )

        with doc.create(Itemize(options=NoEscape("leftmargin=0.0in, label={}"))):
            doc.append(NoEscape(rf"""
            \item
            \begin{{tabularx}}{{\textwidth}}{{Xr}}
            \textbf{{{grad.title}}} ~ {links} \\
            {grad.desc} \\
            \textbf{{Technologies}}: {tech_str}
            \end{{tabularx}}
            """))
            doc.append(NoEscape(COMMON_ITEMS_MINUS_SPACE))


def _build_experience(doc: Document, cv: 'CV'):
    with doc.create(Section("Experience")):
        with doc.create(Itemize(options=NoEscape("leftmargin=0.0in, label={}"))):
            for exp in cv.experiences:
                latex = rf"""
\item
\begin{{tabularx}}{{\textwidth}}{{Xr}}
\textbf{{{exp.title}}} & \textbf{{{exp.date}}} \\
{exp.desc} & {exp.location}
\end{{tabularx}}
"""
                doc.append(NoEscape(latex))
                doc.append(NoEscape(COMMON_ITEMS_MINUS_SPACE))


def _build_course(doc: Document, cv: 'CV'):
    with doc.create(Section("Courses")):
        with doc.create(Itemize(options=NoEscape("leftmargin=0.0in, label={}"))):
            for course in cv.courses:
                latex = rf"""
\item
\begin{{tabularx}}{{\textwidth}}{{Xr}}
\textbf{{{course.title}}} & \textbf{{{course.date}}} \\
{course.desc} & {course.location}
\end{{tabularx}}
"""
                doc.append(NoEscape(latex))
                doc.append(NoEscape(COMMON_ITEMS_MINUS_SPACE))


def _build_project(doc: Document, cv: 'CV'):
    if len(cv.projects) == 0:
        return

    with doc.create(Section("Projects")):
        with doc.create(Itemize(options=NoEscape("leftmargin=0.0in, label={}"))):
            for project in cv.projects:
                # Build the links string side by side with bold + italic text
                links = " ~ ".join(
                    rf"\href{{{url[1]}}}{{\underline{{\textbf{{\textit{{{url[0]}}}}}}}}}" for url in project.urls
                )
                latex = rf"""
\item
\textbf{{{project.title}}} ~ {links} \\
\begin{{tabularx}}{{\linewidth}}{{Xr}}
{project.desc}
\vspace{{-5mm}}
\end{{tabularx}}
"""
                doc.append(NoEscape(latex))
                doc.append(NoEscape(COMMON_ITEMS_MINUS_SPACE))


def _build_volunteering(doc: Document, cv: 'CV'):
    with doc.create(Section("Volunteering")):
        with doc.create(Itemize(options=NoEscape("leftmargin=0.0in, label={}"))):
            for volunteer in cv.volunteers:
                def escape_url(url):
                    return url.replace('&', r'\&').replace('%', r'\%').replace('_', r'\_')

                links = " ~ ".join(
                    rf"\href{{{escape_url(url[1])}}}{{\underline{{\textbf{{\textit{{{escape_url(url[0])}}}}}}}}}"
                    for url in volunteer.urls if len(url) > 1
                )

                latex = rf"""
\item
\begin{{tabularx}}{{\linewidth}}{{X r}}
\textbf{{{volunteer.title}}} ~ {links} & \textbf{{{volunteer.date}}} \\
{volunteer.desc} 
\end{{tabularx}}
\vspace{{1mm}}
                """
                doc.append(NoEscape(latex))
                doc.append(NoEscape(COMMON_ITEMS_MINUS_SPACE))


def _build_tech_skills(doc: Document, cv: 'CV'):
    num_cols = 4

    with doc.create(Section("Technical Skills")):
        latex_table = r"\begin{tabularx}{\textwidth}{"
        latex_table += "X " * num_cols
        latex_table += r"}"

        # Loop over tech skills topics from cv
        for skill_topic in cv.tech_skills:
            skills_i = skill_topic.values
            line_i = rf"\textbf{{{skill_topic.title}}}: " + ", ~ ".join(skills_i) + r". \\"
            latex_table += line_i

        latex_table += r"\end{tabularx}"
        doc.append(NoEscape(latex_table))


def _build_soft_skills(doc: Document, cv: 'CV'):
    num_cols = 3

    with doc.create(Section("Soft Skills")):
        latex_table = r"\begin{tabularx}{\textwidth}{"
        latex_table += "X " * num_cols
        latex_table += r"}"

        # Loop over tech skills from cv
        for i in range(0, len(cv.soft_skills), num_cols):
            row = cv.soft_skills[i:i + num_cols]
            # Pad last row if needed
            while len(row) < num_cols:
                row.append("")
            latex_table += " & ".join(row) + r" \\"  # join row with & and end with \\

        latex_table += r"\end{tabularx}"
        doc.append(NoEscape(latex_table))


def _build_certification(doc: Document, cv: 'CV'):
    if len(cv.certificates) == 0:
        return

    with doc.create(Section("Certificates")):
        with doc.create(Itemize(options=NoEscape("leftmargin=0.0in, label={}"))):

            for cert in cv.certificates:
                latex = rf"""
    \item
    \begin{{tabularx}}{{\textwidth}}{{Xr}}
    \textbf{{{cert.title}}} ~ \href{{{cert.verify}}}{{\underline{{\textbf{{\textit{{Verify}}}}}}}} & \textbf{{{cert.date}}} \\
    {cert.desc} 
    \end{{tabularx}}
    \vspace{{1mm}}
    """
                doc.append(NoEscape(latex))
                doc.append(NoEscape(COMMON_ITEMS_MINUS_SPACE))

            for volunteer in cv.volunteers:
                def escape_url(url):
                    return url.replace('&', r'\&').replace('%', r'\%').replace('_', r'\_')

                links = " ~ ".join(
                    rf"\href{{{escape_url(url[1])}}}{{\underline{{\textbf{{\textit{{{escape_url(url[0])}}}}}}}}}"
                    for url in volunteer.urls if len(url) > 1
                )


def _build_languages(doc: Document, cv: 'CV'):
    with doc.create(Section("Languages")):
        language_entries = []
        for lang in cv.langs:
            language_entries.append(r"\textbf{{{language}}}: {level}".format(
                language=lang.language,
                level=lang.level
            ))
        # Join entries with some spacing
        doc.append(NoEscape(r" \quad ".join(language_entries)))


def _build_additional_experience(doc: Document, cv: 'CV'):
    if len(cv.additional_experience) == 0:
        return

    with doc.create(Section("Additional Experience")):
        with doc.create(Itemize(options=NoEscape("leftmargin=0.0in, label={}"))):
            for exp in cv.additional_experience:
                latex = rf"""
\item
\begin{{tabularx}}{{\textwidth}}{{Xr}}
\textbf{{{exp.title}}}\\
{exp.desc}
\end{{tabularx}}
    """
                doc.append(NoEscape(latex))
                doc.append(NoEscape(COMMON_ITEMS_MINUS_SPACE))
