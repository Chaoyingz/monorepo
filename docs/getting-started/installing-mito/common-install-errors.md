---
description: Common Installation Errors and how to resolve them!
---

# Common Install Errors

{% hint style="info" %}
Want help? [Join our discord for immediate support.](https://discord.com/invite/XdJSZyejJU)
{% endhint %}

## Common Installation Issues

#### The sheet does not render when I call mitosheet.sheet().

This is the most common error, and it is likely because you have failed to refresh your Jupyter. This is usually fixable through the following steps:

1. Shut down the currently running Jupyter instance. Close all browser tabs with Jupyter open.
2. Relaunch Jupyter. Retry calling `mitosheet.sheet()`

If this does not work, try rerunning the installer and repeating the above steps. 

#### The installer hit a PermissionError during install.

If your installation fails with a `PermissionError`, then you likely will be able to successfully install Mito by rerunning the installation commands with adminstrator privileges.

For Windows, this means[ running the command prompt as an admin](https://grok.lsu.edu/article.aspx?articleid=16850), and for Mac/Linux means using the sudo command for the installation commands

#### The installer finished successfully, but the sheet is not rendering when I[ follow the instructions](../../how-to/creating-a-mitosheet/) to create a mitosheet.

This bug can be tricky to resolve. For the best chance of getting sorted, take the following steps:

1. In your browser, open the developer console. This is usually done by pressing `shift+right clicking`, and then clicking the option that includes the word `inspect`.
2. When the developer tab opens up, click the section labeled `console` and scroll to the top. You will likely see a red print out with some error messages.
3. Screen shot those error messages, and send them in an email to jake@sagacollab.com! We'll respond within a few hours, and should be able to get your issues resolved!

**I'm getting an SSL error on MacOSX**

You're probably receiving this error because you need to install the SSL certificates**.**&#x20;

* If you downloaded Python from the official website, then run `/Applications/Python\ 3.9/Install\ Certificates.command` in a terminal (change `3.9` to whatever version you installed).&#x20;
* If you installed Python using MacPorts, run `sudo port install curl-ca-bundle` in a terminal.

If you have any other issues installing Mito, or you're looking to install Mito on JupyterHub or Kuberenetes, [get in touch](https://discord.com/invite/XdJSZyejJU). We'd love to help.

**I do not have Python installed.**

1. [Guide to downloading Python](https://wiki.python.org/moin/BeginnersGuide/Download).

{% hint style="info" %}
Want help? [Get in contact](https://discord.com/invite/XdJSZyejJU) with our support team.
{% endhint %}
