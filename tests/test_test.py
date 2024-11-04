from bs4 import BeautifulSoup

def remove_citations(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for cite in soup.find_all(class_='cite-bracket'):
        cite.decompose()
    for cite_ref in soup.find_all('sup', class_='reference'):
        cite_number = cite_ref.find('span', class_='cite-bracket')
        if cite_number:
            cite_number.extract()
        cite_ref.extract()
    cleaned_html = str(soup)
    return cleaned_html

# Example usage
html_content = """
<table class="toccolours" style="margin: 0 1em 0 1em;" width="50%">

<tbody><tr>
<th align="center" colspan="16" style="background:#E6E6E6"><b>Nemzetiségi eloszlás</b><sup id="cite_ref-113" class="reference"><a href="#cite_note-113"><span class="cite-bracket">[</span>113<span class="cite-bracket">]</span></a></sup>
</th></tr>
<tr>
<th align="center">Időszak
</th>
<th align="center"><span class="mw-image-border noviewer" typeof="mw:File"><a href="/wiki/F%C3%A1jl:Civil_Ensign_of_Hungary.svg" class="mw-file-description" title="Magyar"><img alt="Magyar" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Civil_Ensign_of_Hungary.svg/22px-Civil_Ensign_of_Hungary.svg.png" decoding="async" width="22" height="15" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Civil_Ensign_of_Hungary.svg/33px-Civil_Ensign_of_Hungary.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Civil_Ensign_of_Hungary.svg/44px-Civil_Ensign_of_Hungary.svg.png 2x" data-file-width="900" data-file-height="600"></a></span>
</th>
<th align="center"><span class="mw-image-border noviewer" typeof="mw:File"><a href="/wiki/F%C3%A1jl:Flag_of_Serbia.svg" class="mw-file-description" title="Szerb"><img alt="Szerb" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Flag_of_Serbia.svg/22px-Flag_of_Serbia.svg.png" decoding="async" width="22" height="15" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Flag_of_Serbia.svg/33px-Flag_of_Serbia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Flag_of_Serbia.svg/44px-Flag_of_Serbia.svg.png 2x" data-file-width="1350" data-file-height="900"></a></span>
</th>
<th align="center"><span class="mw-image-border noviewer" typeof="mw:File"><a href="/wiki/F%C3%A1jl:Flag_of_Germany.svg" class="mw-file-description" title="Német"><img alt="Német" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Flag_of_Germany.svg/22px-Flag_of_Germany.svg.png" decoding="async" width="22" height="13" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Flag_of_Germany.svg/33px-Flag_of_Germany.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Flag_of_Germany.svg/44px-Flag_of_Germany.svg.png 2x" data-file-width="1000" data-file-height="600"></a></span>
</th>
<th align="center"><span class="mw-image-border noviewer" typeof="mw:File"><a href="/wiki/F%C3%A1jl:Flag_of_the_Romani_people.svg" class="mw-file-description" title="Romani"><img alt="Romani" src="//upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_the_Romani_people.svg/22px-Flag_of_the_Romani_people.svg.png" decoding="async" width="22" height="15" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_the_Romani_people.svg/33px-Flag_of_the_Romani_people.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_the_Romani_people.svg/44px-Flag_of_the_Romani_people.svg.png 2x" data-file-width="900" data-file-height="600"></a></span>
</th>
<th align="center"><span class="mw-image-border noviewer" typeof="mw:File"><a href="/wiki/F%C3%A1jl:Flag_of_Romania.svg" class="mw-file-description" title="Román"><img alt="Román" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/73/Flag_of_Romania.svg/22px-Flag_of_Romania.svg.png" decoding="async" width="22" height="15" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/7/73/Flag_of_Romania.svg/33px-Flag_of_Romania.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/7/73/Flag_of_Romania.svg/44px-Flag_of_Romania.svg.png 2x" data-file-width="600" data-file-height="400"></a></span>
</th>
<th align="center"><span class="mw-image-border noviewer" typeof="mw:File"><a href="/wiki/F%C3%A1jl:Flag_of_Slovakia.svg" class="mw-file-description" title="Szlovák"><img alt="Szlovák" src="//upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Flag_of_Slovakia.svg/22px-Flag_of_Slovakia.svg.png" decoding="async" width="22" height="15" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Flag_of_Slovakia.svg/33px-Flag_of_Slovakia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Flag_of_Slovakia.svg/44px-Flag_of_Slovakia.svg.png 2x" data-file-width="900" data-file-height="600"></a></span>
</th>
<th align="center">Egyéb/Nem válaszolt
</th>
<th align="center">Összesen
</th></tr>
<tr>
<td align="center">2001
</td>
<td align="center">91,11%
</td>
<td align="center">0,44%
</td>
<td align="center">0,57%
</td>
<td align="center">0,73%
</td>
<td align="center">0,19%
</td>
<td align="center">0,23%
</td>
<td align="center">6,47%
</td>
<td align="center"><b>100%</b>
</td></tr>
<tr>
<td align="center">2011
</td>
<td align="center">79,81%
</td>
<td align="center">0,80%
</td>
<td align="center">0,86%
</td>
<td align="center">0,89%
</td>
<td align="center">0,33%
</td>
<td align="center">0,20%
</td>
<td align="center">16,78%
</td>
<td align="center"><b>100%</b>
</td></tr>
<tr>
<td align="center">2022
</td>
<td align="center">80,51%
</td>
<td align="center">0,89%
</td>
<td align="center">0,72%
</td>
<td align="center">0,66%
</td>
<td align="center">0,25%
</td>
<td align="center">0,14%
</td>
<td align="center">16,42%
</td>
<td align="center"><b>100%</b>
</td></tr></tbody></table>
"""

cleaned_html = remove_citations(html_content)

import pandas as pd

asd = pd.read_html(cleaned_html)
print(cleaned_html)
print(asd[0])