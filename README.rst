============
mordac.quota
============

Clone Package
=============

Clone the mordac.quota git repository::

  $ git clone https://github.com/litsol/mordac.quota.git

Create virtual Python environment::

  $ cd mordac.quota
  $ virtualenv-2.7 .

Activate virtual Python environment::

  $ source bin/activate

Buildout
========

Run buildout::

  $ mkdir -p buildout-cache/{downloads,eggs}
  $ python bootstrap-buildout.py --setuptools-version=8.3
  $ bin/buildout

Run tests::

  $ bin/test
