#!/usr/bin/env python3
import os
import re
import json
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse_frontmatter(content):
    pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.MULTILINE | re.DOTALL)
    match = pattern.search(content)
    if not match:
        return {}
    
    yaml_text = match.group(1)
    metadata = {}
    current_key = None
    list_items = []
    
    for line in yaml_text.splitlines():
        if line.startswith('  - ') or line.startswith('    - '):
            item = line.split('-', 1)[1].strip().strip('"').strip("'")
            list_items.append(item)
            if current_key:
                metadata[current_key] = list_items
        elif ':' in line:
            if current_key and list_items:
                metadata[current_key] = list_items
            list_items = []
            
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            
            if val.startswith('>') or val == '':
                current_key = key
                metadata[current_key] = ""
            else:
                current_key = key
                metadata[current_key] = val.strip('"').strip("'")
        elif current_key and line.strip():
            if isinstance(metadata[current_key], str):
                metadata[current_key] = (metadata[current_key] + " " + line.strip()).strip()
                
    if current_key and list_items:
        metadata[current_key] = list_items
        
    return metadata

def main():
    skills_dir = os.path.join(REPO_ROOT, "skills")
    if not os.path.isdir(skills_dir):
        print(f"Error: skills directory not found at {skills_dir}")
        sys.exit(1)
        
    skills = []
    for d in sorted(os.listdir(skills_dir)):
        d_path = os.path.join(skills_dir, d)
        if not os.path.isdir(d_path):
            continue
        skill_md_path = os.path.join(d_path, "SKILL.md")
        if not os.path.isfile(skill_md_path):
            continue
            
        try:
            with open(skill_md_path, encoding='utf-8') as f:
                content = f.read()
            metadata = parse_frontmatter(content)
            if metadata:
                name = metadata.get("name", d)
                desc = metadata.get("description", "No description")
                category = metadata.get("category", "N/A")
                
                # Normalize triggers
                triggers = metadata.get("triggers", [])
                if isinstance(triggers, str):
                    triggers = [triggers]
                
                trigger = metadata.get("trigger", "")
                if not trigger and triggers:
                    trigger = triggers[0]
                elif not trigger:
                    trigger = f"/{name}"
                    
                skills.append({
                    "name": name,
                    "category": category,
                    "trigger": trigger,
                    "triggers": triggers if triggers else [trigger],
                    "description": desc,
                    "file": f"skills/{d}/SKILL.md"
                })
        except Exception as e:
            print(f"Warning: failed to parse {skill_md_path}: {e}")
            
    if not skills:
        print("No skills found to index.")
        sys.exit(0)
        
    # Write CATALOG.json
    catalog_json = {
        "version": "1.0.0",
        "skills": skills
    }
    
    json_path = os.path.join(skills_dir, "CATALOG.json")
    with open(json_path, "w", encoding='utf-8') as f:
        json.dump(catalog_json, f, indent=2, ensure_ascii=False)
    print(f"Generated {json_path}")
    
    # Write CATALOG.md (zero emoji policy)
    md_content = []
    md_content.append("# Catalogo de Skills de Evol-DD")
    md_content.append("")
    md_content.append("Este catalogo de skills representa la memoria procedal y de razonamiento de Evol-DD. Una skill es una capacidad especializada y reutilizable que los agentes y flujos del sistema pueden invocar para resolver tareas concretas.")
    md_content.append("")
    
    # Categories index
    categories = sorted(list(set(s["category"] for s in skills)))
    md_content.append("## Indice de Categorias")
    md_content.append("")
    for cat in categories:
        md_content.append(f"- {cat.replace('-', ' ').title()}")
    md_content.append("")
    md_content.append("---")
    md_content.append("")
    
    # General table
    md_content.append("## Tabla General de Skills")
    md_content.append("")
    md_content.append("| Nombre | Categoria | Trigger Principal | Descripcion |")
    md_content.append("|--------|-----------|-------------------|-------------|")
    for s in skills:
        link = f"[{s['name']}](file://{os.path.join(REPO_ROOT, s['file'])})"
        md_content.append(f"| {link} | {s['category']} | `{s['trigger']}` | {s['description']} |")
    md_content.append("")
    md_content.append("---")
    md_content.append("")
    
    # Detailed section
    md_content.append("## Detalle por Categoria")
    md_content.append("")
    for cat in categories:
        md_content.append(f"### {cat.replace('-', ' ').title()}")
        md_content.append("")
        cat_skills = [s for s in skills if s["category"] == cat]
        for s in cat_skills:
            link = f"[{s['name']}](file://{os.path.join(REPO_ROOT, s['file'])})"
            md_content.append(f"- **{link}**: {s['description']}")
        md_content.append("")
        
    md_path = os.path.join(skills_dir, "CATALOG.md")
    with open(md_path, "w", encoding='utf-8') as f:
        f.write("\n".join(md_content) + "\n")
    print(f"Generated {md_path}")
    
    # Sync to src/evol_cli/ if directories exist
    cli_skills_dir = os.path.join(REPO_ROOT, "src", "evol_cli", "skills")
    if os.path.isdir(cli_skills_dir):
        import shutil
        shutil.copy2(json_path, os.path.join(cli_skills_dir, "CATALOG.json"))
        shutil.copy2(md_path, os.path.join(cli_skills_dir, "CATALOG.md"))
        print("Mirrored CATALOG files to src/evol_cli/skills/")

if __name__ == "__main__":
    main()
