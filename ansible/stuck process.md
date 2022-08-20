**Stuck process in ansible playbook**

If a process gets stuck then you can launch it in the background and kill it later:

    # git clone hangs but creates .git directory

      - name: Git - clone
        shell: "(git clone git@gitea:marc/gitbackup_{{inventory_hostname}}.git>/dev/null 2>&1 &)"  
        async: 10
        poll: 0
        args:
          chdir: "/tmp"
        environment:
          GIT_SSH_COMMAND: ssh -y -i ~/.ssh/id_git 

      - name: wait for git clone
        shell: sleep 10

      - name: remove old /.git
        file: 
          path: /.git
          state: absent

      - name: move .git to root
        shell: mv /tmp/gitbackup_{{inventory_hostname}}/.git /

      - name: kill rogue git
        shell: kill -9 `pidof git`

      - name: remove old /tmp.git
        file: 
          path: /tmp/gitbackup_{{inventory_hostname}}
          state: absent

      - name: Git - add remote
        shell: git remote add gitea git@gitea:marc/gitbackup_{{inventory_hostname}}.git
        args:
          chdir: "/"


