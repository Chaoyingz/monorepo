---
description: How to install the mitosheet package for Jupyter
---

# Installing Mito

## Before Installing Mito

1. Check that you have **Python 3.6** **or above** by opening a terminal and running `python --version.`

{% hint style="info" %}
By installing Mito, you are agreeing to Mito's [Terms of Service](../../misc/terms-of-service.md) and [Privacy Policy](../../misc/privacy-policy.md). Please review both before installing.
{% endhint %}

## Installing Mito

{% hint style="info" %}
If you wish to install Mito inside of a new virtual environment, you can see[ instructions for installing inside of a virtual environment here.](installing-mito-inside-a-virtual-environment.md)
{% endhint %}

First **open a new terminal or command prompt**. Then, download the Mito installer:

```
python -m pip install mitoinstaller
```

Then, run the installer. This command may take a few moments to run:

```
python -m mitoinstaller install
```

By default, the installer installs Mito for classic Jupyter Notebook as well as JupyterLab. It will automatically launch JupyterLab, but you can also use the Mitosheet package in a Jupyter Notebook.

{% hint style="warning" %}
If you run into errors during installation, check our [common installation errors](common-install-errors.md) to resolve them.
{% endhint %}

If installation completes, proceed to [creating your first Mitosheet.](../../how-to/creating-a-mitosheet/)

{% content-ref url="../../how-to/creating-a-mitosheet/" %}
[creating-a-mitosheet](../../how-to/creating-a-mitosheet/)
{% endcontent-ref %}

{% hint style="info" %}
Our docs (and code) are open source! If you want to suggest changes to the documentation, add some sections, or check out or code, [follow us on Github](https://github.com/mito-ds/monorepo) 
{% endhint %}