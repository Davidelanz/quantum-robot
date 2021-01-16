"""
This file has an example function, with a documentation string which should
serve as a template for quantum-robot docstrings.

Adapted from https://gist.github.com/jakevdp/3808292
"""


def qrobot_template(X, y, a=1, flag=True, f=None, **kwargs):
    """This is where a short one-line description goes

    This is where a longer, multi-line description goes.  It's not
    required, but might be helpful if more information is needed.
    It can also refer to sections below, such as Notes, See Also,
    etc.

    Parameters
    ----------
    X : array_like or sparse matrix
        Array of shape (n_samples, n_features).  Other information about the
        array here.  Keep it to ~2 lines: refer to Notes section for more.

    y : array_like
        Array of shape (n_samples,).  Other information about the
        array here.  Keep it to ~2 lines: refer to Notes section for more.

    a : int (optional, default=1)
        Description of what a does

    flag : bool (optional, default=True)
        If true, then do one thing.
        If false, then do another thing.

    f : callable (optional, default=None)
        Call-back function.  If not specified, then some other function
        will be used

    **kwargs :
        Additional keyword arguments will be passed to name_of_function

    Returns
    -------
    z : ndarray
        result of shape (n_samples,).  Note that here we use "ndarray" rather
        than "array_like", because we assure we'll return a numpy array.

    xmin, xmax : integers
        if multiple parameters have similar description, then they can
        be combined.

    optional_info : dict
        returned only if flag is True.  More info about this return value.

    Examples
    --------
    >>> X = np.ones((4, 3))
    >>> y = np.ones(4)
    >>> qrobot_template(X, y)
    (z, xmin, xmax)  # this should match the actual output

    Notes
    -----
    More information.  This can be in paragraph form, and uses markdown to

    - show lists
    - like this
    - with as many items as you want

    Or to show code blocks, with two colons::

        import pylab as pl
        x = np.arange(10)
        y = np.sin(x)

        pl.plot(x, y)

    We use a code block for a pylab example, because plotting does not
    play well with doctests (doctests runs all the example code, and checks
    that the output matches).

    See Also
    --------
    - numpy.some_related_function : short description (optional)
    - qrobot.some_other_function : short description
    """
    # put the code here
