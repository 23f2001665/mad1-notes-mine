# CSS

CSS is Casading Style Sheet

## CSS Selector

### id Selector (#)

Each element in the page can be uniquely identified by its id(id="something"), id selector targets that specific element to change its style.

### class selector (.)

A group of elements can be grouped together with a class(class="something"), a class can target and apply style to the entire group.

### tag selector (tagname)

A tag can be targetted by its name and style will be applied.

### Universal Selector (*)

Targets everything in the page.

## Location

Whenever the Specificity ties up, location comes into the picture.
Internal CSS > External CSS
Later defined one wins

## Combinations/Operators

- `,` denotes `or` operator which means if any of the given selectors are present apply these styles.
- `.` and `and` operator which means all of the given selectors should be present to get this style.
- ` ` is descendent operator which means `A B` B should be contained within A.
- `>` is a parent operator which means `A>B` B is a direct child of A.
- `~` is a sibling operator which means `A~B` apply the style only if B is next to A