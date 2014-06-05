howto
=====

cheat sheet about howto ....

examples
--------

* query

<pre>
$ howto.py delete git branch
[19:30] ~/.howto/notes.txt
* create a new remote branch on git server
    $ git push origin refs/heads/master:refs/heads/newbranch
    $ git push origin HEAD:refs/heads/experimental
    
    $ git push origin newfeature
    
    Deleting is also a pretty simple task.
    That will delete the newfeature branch on the origin remote
    $ git push origin :newfeature
    
    http://gitready.com/beginner/2009/02/02/push-and-delete-branches.html
</pre>

* edit

  $ vihowto
