Date: 2017-01-26 21:07:28
Title: WorkflowyMd Release Note
Tags: workflowy, userscript
Slug: workflowymd

## What is it?

I've writen several workflowy enhance plugins by UserScript. The very first one is show the full content of the note of a bullet. The second one is to show images under the bullet. Then I worked on the background image to make a more colorful workflowy.

Yeah, workflowy is a powerful tool for noting and orgainizing your knowledge. And it is **FREE**! (Say thankee) And the only drawback of this tool is the text format. 

In the original version of workflowy (without any plugins), we can only add plain text as note for a bullet. It's, of course, less expressive than the rich text notes which we're used to. But now, WorkflowyMd solve that problem.

WorkflowyMd is a suite of usersciprt and stylesheet to enhance the original workflowy with Markdown support. As we know, markdown is one of the most popular lightweight markup language which can create rich text from plain text. We can add headers, images, table, list in the notes, and the original plain text can be fully synced to the server of workflowy. 

Here follows the detail and usage of WorkflowyMd.

## Markdown support

You have to add `[md]` tag at the end of the bullet to let the plugin render your markdown note. If you delete the tag, your note will return to the plain text note.

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/17-1-26/48097654-file_1485411968675_15abe.gif)

## Edit mode

If you want to edit your markdown note. There is no need to type and delete the `[md]` tag every time. Just double click on the note, the notes will toggle between the markdown style (read-only) and plain text style (editable).

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/17-1-26/59010877-file_1485412203554_8eea.gif)

## Better image support

There always one annoy stuff about the image - the size. Sometimes the image size is too large for the page, and some oter time we need an image with full size so we can see every details in the image.

Workflowy solve the problem. The image will be displayed in the style `max-width: 20%` by default. And on a double click, the image will scale to `max-width: 100%` for us to show the details.

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/17-1-26/95527913-file_1485412578590_104ab.gif)

## Syntax Highlight

This is the killer feature for this plugin. Syntax highlight! No more explain, let me show you!

![](https://github.com/Wizmann/assets/raw/master/wizmann-pic/17-1-26/104624-file_1485412763869_931a.gif)

## Get the code

JS: https://github.com/Wizmann/Utils/blob/master/UserScript/WorkflowyMd.js

CSS: https://github.com/Wizmann/Utils/blob/master/UserScript/WorkflowyMd.css

This plugin might conflict with my previous plugins, and I strongly recommand you to drop the previous versions.

If there are bugs in the plguin, please feel free to contact me. (Or you can fix it yourself, it's easy)

## Thanks

This work based on TamperMonkey and Stylish. These two are both commonly used Chrome extension which are easy to get in Chrome App Store. Also, "Markdown-it" is used here for render the markdown notes and "Highlight.js" is used to highlight the source code. And of course, thanks to jQuery to make everything simple.

Have fun with workflowy and WorkflowyMd!

## Special Thanks

Special thanks to Bach and Glenn Gould. :)