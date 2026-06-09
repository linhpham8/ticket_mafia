# QA Improvement Log

Muc tieu: luu memory giua cac sprint theo format machine-readable de AI co the tai su dung nhat quan.

## Quy uoc

- Moi sprint ghi mot section rieng.
- Neu la sprint dau tien hoac khong co baseline sprint truoc, dung `NA` cho delta.
- Khong de trong cac field bat buoc.
- `automated_executed_tc` chi tinh script da duoc execute trong sprint, khong tinh script chi ton tai trong repo.

## Template

```yaml
improvement_snapshot:
  sprint: {project.sprint}
  date: {yyyy-mm-dd}
  modules:
    - module: {module}
      defect_pattern:
        - category: {Functional|Visual|UX|Console|Performance|Accessibility|Content}
          count: {N}
          delta_vs_prev: {+N|-N|0|NA}
      coverage_delta:
        planned_tc: {N}
        executed_tc: {N}
        automated_executed_tc: {N|NA}
        gap: {N|NA}
  top_actions:
    - type: {TC Design|Automation|Process|Environment}
      owner: {role/name}
      action: {specific action}
      due_in_sprint: {Sprint-X}
```

## Sprint Entries

### Sprint: {project.sprint}

```yaml
improvement_snapshot:
  sprint: {project.sprint}
  date: {yyyy-mm-dd}
  modules:
    - module: {module-1}
      defect_pattern:
        - category: {category}
          count: {N}
          delta_vs_prev: {+N|-N|0|NA}
      coverage_delta:
        planned_tc: {N}
        executed_tc: {N}
        automated_executed_tc: {N|NA}
        gap: {N|NA}
  top_actions:
    - type: {TC Design|Automation|Process|Environment}
      owner: {role/name}
      action: {specific action}
      due_in_sprint: {Sprint-X}
```

## Cach dung voi Skill 07/08

- Skill 07 tao block `improvement_snapshot` sau moi daily run/sprint snapshot.
- Skill 08 doc block nay de dien cot `so sprint truoc` va `tin hieu` theo module.
- Cuoi sprint, append block moi vao file nay lam baseline cho sprint tiep theo.
