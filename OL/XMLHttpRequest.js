  


<!DOCTYPE html>
<html>
  <head prefix="og: http://ogp.me/ns# fb: http://ogp.me/ns/fb# githubog: http://ogp.me/ns/fb/githubog#">
    <meta charset='utf-8'>
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>xmlhttprequest/XMLHttpRequest.js at master · ilinsky/xmlhttprequest</title>
    <link rel="search" type="application/opensearchdescription+xml" href="/opensearch.xml" title="GitHub" />
    <link rel="fluid-icon" href="https://github.com/fluidicon.png" title="GitHub" />
    <link rel="apple-touch-icon-precomposed" sizes="57x57" href="apple-touch-icon-114.png" />
    <link rel="apple-touch-icon-precomposed" sizes="114x114" href="apple-touch-icon-114.png" />
    <link rel="apple-touch-icon-precomposed" sizes="72x72" href="apple-touch-icon-144.png" />
    <link rel="apple-touch-icon-precomposed" sizes="144x144" href="apple-touch-icon-144.png" />
    <meta name="msapplication-TileImage" content="/windows-tile.png">
    <meta name="msapplication-TileColor" content="#ffffff">

    
    
    <link rel="icon" type="image/x-icon" href="/favicon.ico" />

    <meta content="authenticity_token" name="csrf-param" />
<meta content="Eo+ZeTXC07mRy8ecxxsLn7wzBNSmljExwRT2KopUXoY=" name="csrf-token" />

    <link href="https://a248.e.akamai.net/assets.github.com/assets/github-2758f9c21ad8bfb88498e4e4f4b78f408b5c5382.css" media="screen" rel="stylesheet" type="text/css" />
    <link href="https://a248.e.akamai.net/assets.github.com/assets/github2-154ffaf2b6e54adc7b4ad61fb3c02fc3faccbd4e.css" media="screen" rel="stylesheet" type="text/css" />
    


    <script src="https://a248.e.akamai.net/assets.github.com/assets/frameworks-28923941200b998a3e7422badab5b9be240f9be4.js" type="text/javascript"></script>
    <script src="https://a248.e.akamai.net/assets.github.com/assets/github-24b8ca996829444ab9173dd22f3e82c8b129e034.js" type="text/javascript"></script>
    

      <link rel='permalink' href='/ilinsky/xmlhttprequest/blob/b5728e32124b44981a19fefb78d6a2a1c3033413/XMLHttpRequest.js'>
    <meta property="og:title" content="xmlhttprequest"/>
    <meta property="og:type" content="githubog:gitrepository"/>
    <meta property="og:url" content="https://github.com/ilinsky/xmlhttprequest"/>
    <meta property="og:image" content="https://a248.e.akamai.net/assets.github.com/images/gravatars/gravatar-user-420.png?1345673561"/>
    <meta property="og:site_name" content="GitHub"/>
    <meta property="og:description" content="xmlhttprequest - XMLHttpRequest.js - Standard-compliant cross-browser XMLHttpRequest object implementation"/>

    <meta name="description" content="xmlhttprequest - XMLHttpRequest.js - Standard-compliant cross-browser XMLHttpRequest object implementation" />
  <link href="https://github.com/ilinsky/xmlhttprequest/commits/master.atom" rel="alternate" title="Recent Commits to xmlhttprequest:master" type="application/atom+xml" />

  </head>


  <body class="logged_in page-blob windows vis-public env-production ">
    <div id="wrapper">

    
    

    
  <div id="unsupported-browser">
    <div class="container clearfix">
      <a href="https://help.github.com/articles/supported-browsers" class="button classy">Learn More</a>
      <h5>Please note that GitHub no longer supports Internet Explorer versions 7 or 8.</h5>
      <p>We recommend upgrading to <a href="http://ie.microsoft.com/">Internet Explorer 9</a>, <a href="http://chrome.google.com">Google Chrome</a>, or <a href="http://mozilla.org/firefox/">Firefox</a>.</p>
    </div>
  </div>


      <div id="header" class="true clearfix">
        <div class="container clearfix">
          <a class="site-logo " href="https://github.com/">
            <img alt="GitHub" class="github-logo-4x" height="30" src="https://a248.e.akamai.net/assets.github.com/images/modules/header/logov7@4x.png?1340659511" />
            <img alt="GitHub" class="github-logo-4x-hover" height="30" src="https://a248.e.akamai.net/assets.github.com/images/modules/header/logov7@4x-hover.png?1340659511" />
          </a>

            <a href="/notifications" class="notification-indicator tooltipped downwards" title="You have no unread notifications">
              <span class="mail-status all-read"></span>
            </a>

              
    <div class="topsearch command-bar-activated">
      <form accept-charset="UTF-8" action="/search" class="command_bar_form" id="top_search_form" method="get">
  <a href="/search" class="advanced-search tooltipped downwards command-bar-search" id="advanced_search" title="Advanced Search"><span class="mini-icon mini-icon-advanced-search "></span></a>
  <input type="text" name="q" id="command-bar" placeholder="Search or Type a Command" tabindex="1" data-username="cses" autocapitalize="off" />
  <span class="mini-icon help tooltipped downwards" title="Show Command Bar Help"></span>
  <input type="hidden" name="type" value="Everything" />
  <input type="hidden" name="repo" value="" />
  <input type="hidden" name="langOverride" value="" />
  <input type="hidden" name="start_value" value="1" />
</form>

      <ul class="top-nav">
          <li class="explore"><a href="https://github.com/explore">Explore</a></li>
          <li><a href="https://gist.github.com">Gist</a></li>
          <li><a href="/blog">Blog</a></li>
        <li><a href="http://help.github.com">Help</a></li>
      </ul>
    </div>


            

  
  <div id="userbox">
    <div id="user">
      <a href="https://github.com/cses"><img height="20" src="https://secure.gravatar.com/avatar/c7e651193b645fcc52ee3df35327d250?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>
      <a href="https://github.com/cses" class="name">cses</a>
    </div>
    <ul id="user-links">
      <li>
        <a href="/new" id="new_repo" class="tooltipped downwards" title="Create a New Repo"><span class="mini-icon mini-icon-create"></span></a>
      </li>
      <li>
        <a href="/settings/profile" id="account_settings"
          class="tooltipped downwards"
          title="Account Settings (You have no verified emails)">
          <span class="mini-icon mini-icon-account-settings"></span>
            <span class="setting_warning">!</span>
        </a>
      </li>
      <li>
          <a href="/logout" data-method="post" id="logout" class="tooltipped downwards" title="Sign Out">
            <span class="mini-icon mini-icon-logout"></span>
          </a>
      </li>
    </ul>
  </div>



          
        </div>
      </div>

      <div class="global-notice warn"><div class="global-notice-inner"><h2>You don't have any verified emails.  We recommend <a href="https://github.com/settings/emails">verifying</a> at least one email.</h2><p>Email verification will help our support team help you in case you have any email issues or lose your password.</p></div></div>

      


            <div class="site hfeed" itemscope itemtype="http://schema.org/WebPage">
      <div class="hentry">
        
        <div class="pagehead repohead instapaper_ignore readability-menu">
          <div class="container">
            <div class="title-actions-bar">
              


                  <ul class="pagehead-actions">

          <li class="subscription">
              <form accept-charset="UTF-8" action="/notifications/subscribe" data-autosubmit="true" data-remote="true" method="post"><div style="margin:0;padding:0;display:inline"><input name="authenticity_token" type="hidden" value="Eo+ZeTXC07mRy8ecxxsLn7wzBNSmljExwRT2KopUXoY=" /></div>  <input id="repository_id" name="repository_id" type="hidden" value="1722457" />
  <div class="context-menu-container js-menu-container js-context-menu">
    <span class="minibutton switcher bigger js-menu-target">
      <span class="js-context-button">
          <span class="mini-icon mini-icon-watching"></span>Watch
      </span>
    </span>

    <div class="context-pane js-menu-content">
      <a href="javascript:;" class="close js-menu-close"><span class="mini-icon mini-icon-remove-close"></span></a>
      <div class="context-title">Notification status</div>

      <div class="context-body pane-selector">
        <ul class="js-navigation-container">
          <li class="selector-item js-navigation-item js-navigation-target selected">
            <span class="mini-icon mini-icon-confirm"></span>
            <label>
              <input checked="checked" id="do_included" name="do" type="radio" value="included" />
              <h4>Not watching</h4>
              <p>You will only receive notifications when you participate or are mentioned.</p>
            </label>
            <span class="context-button-text js-context-button-text">
              <span class="mini-icon mini-icon-watching"></span>
              Watch
            </span>
          </li>
          <li class="selector-item js-navigation-item js-navigation-target ">
            <span class="mini-icon mini-icon-confirm"></span>
            <label>
              <input id="do_subscribed" name="do" type="radio" value="subscribed" />
              <h4>Watching</h4>
              <p>You will receive all notifications for this repository.</p>
            </label>
            <span class="context-button-text js-context-button-text">
              <span class="mini-icon mini-icon-unwatch"></span>
              Unwatch
            </span>
          </li>
          <li class="selector-item js-navigation-item js-navigation-target ">
            <span class="mini-icon mini-icon-confirm"></span>
            <label>
              <input id="do_ignore" name="do" type="radio" value="ignore" />
              <h4>Ignored</h4>
              <p>You will not receive notifications for this repository.</p>
            </label>
            <span class="context-button-text js-context-button-text">
              <span class="mini-icon mini-icon-mute"></span>
              Stop ignoring
            </span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</form>
          </li>

          <li class="js-toggler-container js-social-container starring-container ">
            <a href="/ilinsky/xmlhttprequest/unstar" class="minibutton js-toggler-target starred" data-remote="true" data-method="post" rel="nofollow">
              <span class="mini-icon mini-icon-star"></span>Unstar
            </a><a href="/ilinsky/xmlhttprequest/star" class="minibutton js-toggler-target unstarred" data-remote="true" data-method="post" rel="nofollow">
              <span class="mini-icon mini-icon-star"></span>Star
            </a><a class="social-count js-social-count" href="/ilinsky/xmlhttprequest/stargazers">62</a>
          </li>

              <li>
                <a href="/ilinsky/xmlhttprequest/fork_select" class="minibutton js-toggler-target lighter" rel="facebox nofollow"><span class="mini-icon mini-icon-fork"></span>Fork</a><a href="/ilinsky/xmlhttprequest/network" class="social-count">10</a>
              </li>


    </ul>

              <h1 itemscope itemtype="http://data-vocabulary.org/Breadcrumb" class="entry-title public">
                <span class="repo-label"><span>public</span></span>
                <span class="mega-icon mega-icon-public-repo"></span>
                <span class="author vcard">
                  <a href="/ilinsky" class="url fn" itemprop="url" rel="author">
                  <span itemprop="title">ilinsky</span>
                  </a></span> /
                <strong><a href="/ilinsky/xmlhttprequest" class="js-current-repository">xmlhttprequest</a></strong>
              </h1>
            </div>

            

  <ul class="tabs">
    <li><a href="/ilinsky/xmlhttprequest" class="selected" highlight="repo_sourcerepo_downloadsrepo_commitsrepo_tagsrepo_branches">Code</a></li>
    <li><a href="/ilinsky/xmlhttprequest/network" highlight="repo_network">Network</a></li>
    <li><a href="/ilinsky/xmlhttprequest/pulls" highlight="repo_pulls">Pull Requests <span class='counter'>0</span></a></li>

      <li><a href="/ilinsky/xmlhttprequest/issues" highlight="repo_issues">Issues <span class='counter'>3</span></a></li>

      <li><a href="/ilinsky/xmlhttprequest/wiki" highlight="repo_wiki">Wiki</a></li>


    <li><a href="/ilinsky/xmlhttprequest/graphs" highlight="repo_graphsrepo_contributors">Graphs</a></li>


  </ul>
  
  <div class="frame frame-center tree-finder" style="display:none"
      data-tree-list-url="/ilinsky/xmlhttprequest/tree-list/b5728e32124b44981a19fefb78d6a2a1c3033413"
      data-blob-url-prefix="/ilinsky/xmlhttprequest/blob/master">

  <div class="breadcrumb">
    <span class="bold"><a href="/ilinsky/xmlhttprequest">xmlhttprequest</a></span> /
    <input class="tree-finder-input js-navigation-enable" type="text" name="query" autocomplete="off" spellcheck="false">
  </div>

    <div class="octotip">
      <p>
        <a href="/ilinsky/xmlhttprequest/dismiss-tree-finder-help" class="dismiss js-dismiss-tree-list-help" title="Hide this notice forever" rel="nofollow">Dismiss</a>
        <span class="bold">Octotip:</span> You've activated the <em>file finder</em>
        by pressing <span class="kbd">t</span> Start typing to filter the
        file list. Use <span class="kbd badmono">↑</span> and
        <span class="kbd badmono">↓</span> to navigate,
        <span class="kbd">enter</span> to view files.
      </p>
    </div>

  <table class="tree-browser css-truncate" cellpadding="0" cellspacing="0">
    <tr class="js-no-results no-results" style="display: none">
      <th colspan="2">No matching files</th>
    </tr>
    <tbody class="js-results-list js-navigation-container">
    </tbody>
  </table>
</div>

<div id="jump-to-line" style="display:none">
  <h2>Jump to Line</h2>
  <form accept-charset="UTF-8">
    <input class="textfield" type="text">
    <div class="full-button">
      <button type="submit" class="classy">
        Go
      </button>
    </div>
  </form>
</div>


<div class="tabnav">

  <span class="tabnav-right">
    <ul class="tabnav-tabs">
      <li><a href="/ilinsky/xmlhttprequest/tags" class="tabnav-tab" highlight="repo_tags">Tags <span class="counter blank">0</span></a></li>
      <li><a href="/ilinsky/xmlhttprequest/downloads" class="tabnav-tab" highlight="repo_downloads">Downloads <span class="counter blank">0</span></a></li>
    </ul>
    
  </span>

  <div class="tabnav-widget scope">


    <div class="context-menu-container js-menu-container js-context-menu">
      <a href="#"
         class="minibutton bigger switcher js-menu-target js-commitish-button btn-branch repo-tree"
         data-hotkey="w"
         data-ref="master">
         <span><em class="mini-icon mini-icon-branch"></em><i>branch:</i> master</span>
      </a>

      <div class="context-pane commitish-context js-menu-content">
        <a href="javascript:;" class="close js-menu-close"><span class="mini-icon mini-icon-remove-close"></span></a>
        <div class="context-title">Switch branches/tags</div>
        <div class="context-body pane-selector commitish-selector js-navigation-container">
          <div class="filterbar">
            <input type="text" id="context-commitish-filter-field" class="js-navigation-enable js-filterable-field" placeholder="Filter branches/tags">
            <ul class="tabs">
              <li><a href="#" data-filter="branches" class="selected">Branches</a></li>
                <li><a href="#" data-filter="tags">Tags</a></li>
            </ul>
          </div>

          <div class="js-filter-tab js-filter-branches" data-filterable-for="context-commitish-filter-field" data-filterable-type=substring>
            <div class="no-results js-not-filterable">Nothing to show</div>
              <div class="commitish-item branch-commitish selector-item js-navigation-item js-navigation-target selected">
                <span class="mini-icon mini-icon-confirm"></span>
                <h4>
                    <a href="/ilinsky/xmlhttprequest/blob/master/XMLHttpRequest.js" class="js-navigation-open" data-name="master" rel="nofollow">master</a>
                </h4>
              </div>
          </div>

            <div class="js-filter-tab js-filter-tags filter-tab-empty" style="display:none" data-filterable-for="context-commitish-filter-field" data-filterable-type=substring>
              <div class="no-results js-not-filterable">Nothing to show</div>
            </div>
        </div>
      </div><!-- /.commitish-context-context -->
    </div>
  </div> <!-- /.scope -->

  <ul class="tabnav-tabs">
    <li><a href="/ilinsky/xmlhttprequest" class="selected tabnav-tab" highlight="repo_source">Files</a></li>
    <li><a href="/ilinsky/xmlhttprequest/commits/master" class="tabnav-tab" highlight="repo_commits">Commits</a></li>
    <li><a href="/ilinsky/xmlhttprequest/branches" class="tabnav-tab" highlight="repo_branches" rel="nofollow">Branches <span class="counter ">1</span></a></li>
  </ul>

</div>

  
  
  


            
          </div>
        </div><!-- /.repohead -->

        <div id="js-repo-pjax-container" class="container context-loader-container" data-pjax-container>
          


<!-- blob contrib key: blob_contributors:v21:50fe858e19d8be7e5b859f15a06454dd -->
<!-- blob contrib frag key: views10/v8/blob_contributors:v21:50fe858e19d8be7e5b859f15a06454dd -->

<div id="slider">


    <p title="This is a placeholder element" class="js-history-link-replace hidden"></p>
    <div class="breadcrumb" data-path="XMLHttpRequest.js/">
      <b itemscope="" itemtype="http://data-vocabulary.org/Breadcrumb"><a href="/ilinsky/xmlhttprequest" itemscope="url"><span itemprop="title">xmlhttprequest</span></a></b> / <strong class="final-path">XMLHttpRequest.js</strong> <span class="js-clippy mini-icon mini-icon-clippy " data-clipboard-text="XMLHttpRequest.js" data-copied-hint="copied!" data-copy-hint="copy to clipboard"></span>
    </div>

      
  <div class="commit file-history-tease js-blob-contributors-content" data-path="XMLHttpRequest.js/">
    <img class="main-avatar" height="24" src="https://secure.gravatar.com/avatar/03521f472d4ac14a98df8deb5ed19e64?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
    <span class="author"><a href="/HelderMagalhaes">HelderMagalhaes</a></span>
    <time class="js-relative-date" datetime="2012-08-06T23:57:55-07:00" title="2012-08-06 23:57:55">August 06, 2012</time>
    <div class="commit-title">
        <a href="/ilinsky/xmlhttprequest/commit/31b310965dcb3a407cf5a1f670c32866ea73422c" class="message">Fix typo and remove trailing space.</a>
    </div>

    <div class="participation">
      <p class="quickstat"><a href="#blob_contributors_box" rel="facebox"><strong>5</strong> contributors</a></p>
          <a class="avatar tooltipped downwards" title="HelderMagalhaes" href="/ilinsky/xmlhttprequest/commits/master/XMLHttpRequest.js?author=HelderMagalhaes"><img height="20" src="https://secure.gravatar.com/avatar/03521f472d4ac14a98df8deb5ed19e64?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>
    <a class="avatar tooltipped downwards" title="dmp42" href="/ilinsky/xmlhttprequest/commits/master/XMLHttpRequest.js?author=dmp42"><img height="20" src="https://secure.gravatar.com/avatar/05e919c31cc2eee4c441e5db21be2df3?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>
    <a class="avatar tooltipped downwards" title="ilinsky" href="/ilinsky/xmlhttprequest/commits/master/XMLHttpRequest.js?author=ilinsky"><img height="20" src="https://secure.gravatar.com/avatar/b79bbc8a593b79650ac7be8d44a9f4f3?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>
    <a class="avatar tooltipped downwards" title="marijn" href="/ilinsky/xmlhttprequest/commits/master/XMLHttpRequest.js?author=marijn"><img height="20" src="https://secure.gravatar.com/avatar/c95d7a7a5b331b7c42d38d96453f47cc?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>
    <a class="avatar tooltipped downwards" title="scotmcc" href="/ilinsky/xmlhttprequest/commits/master/XMLHttpRequest.js?author=scotmcc"><img height="20" src="https://secure.gravatar.com/avatar/9ffbeaf8ac81fc20aebf08e4c3ed4a9d?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="20" /></a>


    </div>
    <div id="blob_contributors_box" style="display:none">
      <h2>Users on GitHub who have contributed to this file</h2>
      <ul class="facebox-user-list">
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/03521f472d4ac14a98df8deb5ed19e64?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/HelderMagalhaes">HelderMagalhaes</a>
        </li>
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/05e919c31cc2eee4c441e5db21be2df3?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/dmp42">dmp42</a>
        </li>
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/b79bbc8a593b79650ac7be8d44a9f4f3?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/ilinsky">ilinsky</a>
        </li>
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/c95d7a7a5b331b7c42d38d96453f47cc?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/marijn">marijn</a>
        </li>
        <li>
          <img height="24" src="https://secure.gravatar.com/avatar/9ffbeaf8ac81fc20aebf08e4c3ed4a9d?s=140&amp;d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png" width="24" />
          <a href="/scotmcc">scotmcc</a>
        </li>
      </ul>
    </div>
  </div>


    <div class="frames">
      <div class="frame frame-center" data-path="XMLHttpRequest.js/" data-permalink-url="/ilinsky/xmlhttprequest/blob/b5728e32124b44981a19fefb78d6a2a1c3033413/XMLHttpRequest.js" data-title="xmlhttprequest/XMLHttpRequest.js at master · ilinsky/xmlhttprequest · GitHub" data-type="blob">

        <div id="files" class="bubble">
          <div class="file">
            <div class="meta">
              <div class="info">
                <span class="icon"><b class="mini-icon mini-icon-text-file"></b></span>
                <span class="mode" title="File Mode">executable file</span>
                  <span>526 lines (450 sloc)</span>
                <span>15.58 kb</span>
              </div>
              <ul class="button-group actions">
                  <li>
                    <a class="grouped-button file-edit-link minibutton bigger lighter" href="/ilinsky/xmlhttprequest/edit/master/XMLHttpRequest.js" data-method="post" rel="nofollow" data-hotkey="e">Edit</a>
                  </li>
                <li>
                  <a href="/ilinsky/xmlhttprequest/raw/master/XMLHttpRequest.js" class="minibutton grouped-button bigger lighter" id="raw-url">Raw</a>
                </li>
                  <li>
                    <a href="/ilinsky/xmlhttprequest/blame/master/XMLHttpRequest.js" class="minibutton grouped-button bigger lighter">Blame</a>
                  </li>
                <li>
                  <a href="/ilinsky/xmlhttprequest/commits/master/XMLHttpRequest.js" class="minibutton grouped-button bigger lighter" rel="nofollow">History</a>
                </li>
              </ul>
            </div>
                <div class="data type-javascript">
      <table cellpadding="0" cellspacing="0" class="lines">
        <tr>
          <td>
            <pre class="line_numbers"><span id="L1" rel="#L1">1</span>
<span id="L2" rel="#L2">2</span>
<span id="L3" rel="#L3">3</span>
<span id="L4" rel="#L4">4</span>
<span id="L5" rel="#L5">5</span>
<span id="L6" rel="#L6">6</span>
<span id="L7" rel="#L7">7</span>
<span id="L8" rel="#L8">8</span>
<span id="L9" rel="#L9">9</span>
<span id="L10" rel="#L10">10</span>
<span id="L11" rel="#L11">11</span>
<span id="L12" rel="#L12">12</span>
<span id="L13" rel="#L13">13</span>
<span id="L14" rel="#L14">14</span>
<span id="L15" rel="#L15">15</span>
<span id="L16" rel="#L16">16</span>
<span id="L17" rel="#L17">17</span>
<span id="L18" rel="#L18">18</span>
<span id="L19" rel="#L19">19</span>
<span id="L20" rel="#L20">20</span>
<span id="L21" rel="#L21">21</span>
<span id="L22" rel="#L22">22</span>
<span id="L23" rel="#L23">23</span>
<span id="L24" rel="#L24">24</span>
<span id="L25" rel="#L25">25</span>
<span id="L26" rel="#L26">26</span>
<span id="L27" rel="#L27">27</span>
<span id="L28" rel="#L28">28</span>
<span id="L29" rel="#L29">29</span>
<span id="L30" rel="#L30">30</span>
<span id="L31" rel="#L31">31</span>
<span id="L32" rel="#L32">32</span>
<span id="L33" rel="#L33">33</span>
<span id="L34" rel="#L34">34</span>
<span id="L35" rel="#L35">35</span>
<span id="L36" rel="#L36">36</span>
<span id="L37" rel="#L37">37</span>
<span id="L38" rel="#L38">38</span>
<span id="L39" rel="#L39">39</span>
<span id="L40" rel="#L40">40</span>
<span id="L41" rel="#L41">41</span>
<span id="L42" rel="#L42">42</span>
<span id="L43" rel="#L43">43</span>
<span id="L44" rel="#L44">44</span>
<span id="L45" rel="#L45">45</span>
<span id="L46" rel="#L46">46</span>
<span id="L47" rel="#L47">47</span>
<span id="L48" rel="#L48">48</span>
<span id="L49" rel="#L49">49</span>
<span id="L50" rel="#L50">50</span>
<span id="L51" rel="#L51">51</span>
<span id="L52" rel="#L52">52</span>
<span id="L53" rel="#L53">53</span>
<span id="L54" rel="#L54">54</span>
<span id="L55" rel="#L55">55</span>
<span id="L56" rel="#L56">56</span>
<span id="L57" rel="#L57">57</span>
<span id="L58" rel="#L58">58</span>
<span id="L59" rel="#L59">59</span>
<span id="L60" rel="#L60">60</span>
<span id="L61" rel="#L61">61</span>
<span id="L62" rel="#L62">62</span>
<span id="L63" rel="#L63">63</span>
<span id="L64" rel="#L64">64</span>
<span id="L65" rel="#L65">65</span>
<span id="L66" rel="#L66">66</span>
<span id="L67" rel="#L67">67</span>
<span id="L68" rel="#L68">68</span>
<span id="L69" rel="#L69">69</span>
<span id="L70" rel="#L70">70</span>
<span id="L71" rel="#L71">71</span>
<span id="L72" rel="#L72">72</span>
<span id="L73" rel="#L73">73</span>
<span id="L74" rel="#L74">74</span>
<span id="L75" rel="#L75">75</span>
<span id="L76" rel="#L76">76</span>
<span id="L77" rel="#L77">77</span>
<span id="L78" rel="#L78">78</span>
<span id="L79" rel="#L79">79</span>
<span id="L80" rel="#L80">80</span>
<span id="L81" rel="#L81">81</span>
<span id="L82" rel="#L82">82</span>
<span id="L83" rel="#L83">83</span>
<span id="L84" rel="#L84">84</span>
<span id="L85" rel="#L85">85</span>
<span id="L86" rel="#L86">86</span>
<span id="L87" rel="#L87">87</span>
<span id="L88" rel="#L88">88</span>
<span id="L89" rel="#L89">89</span>
<span id="L90" rel="#L90">90</span>
<span id="L91" rel="#L91">91</span>
<span id="L92" rel="#L92">92</span>
<span id="L93" rel="#L93">93</span>
<span id="L94" rel="#L94">94</span>
<span id="L95" rel="#L95">95</span>
<span id="L96" rel="#L96">96</span>
<span id="L97" rel="#L97">97</span>
<span id="L98" rel="#L98">98</span>
<span id="L99" rel="#L99">99</span>
<span id="L100" rel="#L100">100</span>
<span id="L101" rel="#L101">101</span>
<span id="L102" rel="#L102">102</span>
<span id="L103" rel="#L103">103</span>
<span id="L104" rel="#L104">104</span>
<span id="L105" rel="#L105">105</span>
<span id="L106" rel="#L106">106</span>
<span id="L107" rel="#L107">107</span>
<span id="L108" rel="#L108">108</span>
<span id="L109" rel="#L109">109</span>
<span id="L110" rel="#L110">110</span>
<span id="L111" rel="#L111">111</span>
<span id="L112" rel="#L112">112</span>
<span id="L113" rel="#L113">113</span>
<span id="L114" rel="#L114">114</span>
<span id="L115" rel="#L115">115</span>
<span id="L116" rel="#L116">116</span>
<span id="L117" rel="#L117">117</span>
<span id="L118" rel="#L118">118</span>
<span id="L119" rel="#L119">119</span>
<span id="L120" rel="#L120">120</span>
<span id="L121" rel="#L121">121</span>
<span id="L122" rel="#L122">122</span>
<span id="L123" rel="#L123">123</span>
<span id="L124" rel="#L124">124</span>
<span id="L125" rel="#L125">125</span>
<span id="L126" rel="#L126">126</span>
<span id="L127" rel="#L127">127</span>
<span id="L128" rel="#L128">128</span>
<span id="L129" rel="#L129">129</span>
<span id="L130" rel="#L130">130</span>
<span id="L131" rel="#L131">131</span>
<span id="L132" rel="#L132">132</span>
<span id="L133" rel="#L133">133</span>
<span id="L134" rel="#L134">134</span>
<span id="L135" rel="#L135">135</span>
<span id="L136" rel="#L136">136</span>
<span id="L137" rel="#L137">137</span>
<span id="L138" rel="#L138">138</span>
<span id="L139" rel="#L139">139</span>
<span id="L140" rel="#L140">140</span>
<span id="L141" rel="#L141">141</span>
<span id="L142" rel="#L142">142</span>
<span id="L143" rel="#L143">143</span>
<span id="L144" rel="#L144">144</span>
<span id="L145" rel="#L145">145</span>
<span id="L146" rel="#L146">146</span>
<span id="L147" rel="#L147">147</span>
<span id="L148" rel="#L148">148</span>
<span id="L149" rel="#L149">149</span>
<span id="L150" rel="#L150">150</span>
<span id="L151" rel="#L151">151</span>
<span id="L152" rel="#L152">152</span>
<span id="L153" rel="#L153">153</span>
<span id="L154" rel="#L154">154</span>
<span id="L155" rel="#L155">155</span>
<span id="L156" rel="#L156">156</span>
<span id="L157" rel="#L157">157</span>
<span id="L158" rel="#L158">158</span>
<span id="L159" rel="#L159">159</span>
<span id="L160" rel="#L160">160</span>
<span id="L161" rel="#L161">161</span>
<span id="L162" rel="#L162">162</span>
<span id="L163" rel="#L163">163</span>
<span id="L164" rel="#L164">164</span>
<span id="L165" rel="#L165">165</span>
<span id="L166" rel="#L166">166</span>
<span id="L167" rel="#L167">167</span>
<span id="L168" rel="#L168">168</span>
<span id="L169" rel="#L169">169</span>
<span id="L170" rel="#L170">170</span>
<span id="L171" rel="#L171">171</span>
<span id="L172" rel="#L172">172</span>
<span id="L173" rel="#L173">173</span>
<span id="L174" rel="#L174">174</span>
<span id="L175" rel="#L175">175</span>
<span id="L176" rel="#L176">176</span>
<span id="L177" rel="#L177">177</span>
<span id="L178" rel="#L178">178</span>
<span id="L179" rel="#L179">179</span>
<span id="L180" rel="#L180">180</span>
<span id="L181" rel="#L181">181</span>
<span id="L182" rel="#L182">182</span>
<span id="L183" rel="#L183">183</span>
<span id="L184" rel="#L184">184</span>
<span id="L185" rel="#L185">185</span>
<span id="L186" rel="#L186">186</span>
<span id="L187" rel="#L187">187</span>
<span id="L188" rel="#L188">188</span>
<span id="L189" rel="#L189">189</span>
<span id="L190" rel="#L190">190</span>
<span id="L191" rel="#L191">191</span>
<span id="L192" rel="#L192">192</span>
<span id="L193" rel="#L193">193</span>
<span id="L194" rel="#L194">194</span>
<span id="L195" rel="#L195">195</span>
<span id="L196" rel="#L196">196</span>
<span id="L197" rel="#L197">197</span>
<span id="L198" rel="#L198">198</span>
<span id="L199" rel="#L199">199</span>
<span id="L200" rel="#L200">200</span>
<span id="L201" rel="#L201">201</span>
<span id="L202" rel="#L202">202</span>
<span id="L203" rel="#L203">203</span>
<span id="L204" rel="#L204">204</span>
<span id="L205" rel="#L205">205</span>
<span id="L206" rel="#L206">206</span>
<span id="L207" rel="#L207">207</span>
<span id="L208" rel="#L208">208</span>
<span id="L209" rel="#L209">209</span>
<span id="L210" rel="#L210">210</span>
<span id="L211" rel="#L211">211</span>
<span id="L212" rel="#L212">212</span>
<span id="L213" rel="#L213">213</span>
<span id="L214" rel="#L214">214</span>
<span id="L215" rel="#L215">215</span>
<span id="L216" rel="#L216">216</span>
<span id="L217" rel="#L217">217</span>
<span id="L218" rel="#L218">218</span>
<span id="L219" rel="#L219">219</span>
<span id="L220" rel="#L220">220</span>
<span id="L221" rel="#L221">221</span>
<span id="L222" rel="#L222">222</span>
<span id="L223" rel="#L223">223</span>
<span id="L224" rel="#L224">224</span>
<span id="L225" rel="#L225">225</span>
<span id="L226" rel="#L226">226</span>
<span id="L227" rel="#L227">227</span>
<span id="L228" rel="#L228">228</span>
<span id="L229" rel="#L229">229</span>
<span id="L230" rel="#L230">230</span>
<span id="L231" rel="#L231">231</span>
<span id="L232" rel="#L232">232</span>
<span id="L233" rel="#L233">233</span>
<span id="L234" rel="#L234">234</span>
<span id="L235" rel="#L235">235</span>
<span id="L236" rel="#L236">236</span>
<span id="L237" rel="#L237">237</span>
<span id="L238" rel="#L238">238</span>
<span id="L239" rel="#L239">239</span>
<span id="L240" rel="#L240">240</span>
<span id="L241" rel="#L241">241</span>
<span id="L242" rel="#L242">242</span>
<span id="L243" rel="#L243">243</span>
<span id="L244" rel="#L244">244</span>
<span id="L245" rel="#L245">245</span>
<span id="L246" rel="#L246">246</span>
<span id="L247" rel="#L247">247</span>
<span id="L248" rel="#L248">248</span>
<span id="L249" rel="#L249">249</span>
<span id="L250" rel="#L250">250</span>
<span id="L251" rel="#L251">251</span>
<span id="L252" rel="#L252">252</span>
<span id="L253" rel="#L253">253</span>
<span id="L254" rel="#L254">254</span>
<span id="L255" rel="#L255">255</span>
<span id="L256" rel="#L256">256</span>
<span id="L257" rel="#L257">257</span>
<span id="L258" rel="#L258">258</span>
<span id="L259" rel="#L259">259</span>
<span id="L260" rel="#L260">260</span>
<span id="L261" rel="#L261">261</span>
<span id="L262" rel="#L262">262</span>
<span id="L263" rel="#L263">263</span>
<span id="L264" rel="#L264">264</span>
<span id="L265" rel="#L265">265</span>
<span id="L266" rel="#L266">266</span>
<span id="L267" rel="#L267">267</span>
<span id="L268" rel="#L268">268</span>
<span id="L269" rel="#L269">269</span>
<span id="L270" rel="#L270">270</span>
<span id="L271" rel="#L271">271</span>
<span id="L272" rel="#L272">272</span>
<span id="L273" rel="#L273">273</span>
<span id="L274" rel="#L274">274</span>
<span id="L275" rel="#L275">275</span>
<span id="L276" rel="#L276">276</span>
<span id="L277" rel="#L277">277</span>
<span id="L278" rel="#L278">278</span>
<span id="L279" rel="#L279">279</span>
<span id="L280" rel="#L280">280</span>
<span id="L281" rel="#L281">281</span>
<span id="L282" rel="#L282">282</span>
<span id="L283" rel="#L283">283</span>
<span id="L284" rel="#L284">284</span>
<span id="L285" rel="#L285">285</span>
<span id="L286" rel="#L286">286</span>
<span id="L287" rel="#L287">287</span>
<span id="L288" rel="#L288">288</span>
<span id="L289" rel="#L289">289</span>
<span id="L290" rel="#L290">290</span>
<span id="L291" rel="#L291">291</span>
<span id="L292" rel="#L292">292</span>
<span id="L293" rel="#L293">293</span>
<span id="L294" rel="#L294">294</span>
<span id="L295" rel="#L295">295</span>
<span id="L296" rel="#L296">296</span>
<span id="L297" rel="#L297">297</span>
<span id="L298" rel="#L298">298</span>
<span id="L299" rel="#L299">299</span>
<span id="L300" rel="#L300">300</span>
<span id="L301" rel="#L301">301</span>
<span id="L302" rel="#L302">302</span>
<span id="L303" rel="#L303">303</span>
<span id="L304" rel="#L304">304</span>
<span id="L305" rel="#L305">305</span>
<span id="L306" rel="#L306">306</span>
<span id="L307" rel="#L307">307</span>
<span id="L308" rel="#L308">308</span>
<span id="L309" rel="#L309">309</span>
<span id="L310" rel="#L310">310</span>
<span id="L311" rel="#L311">311</span>
<span id="L312" rel="#L312">312</span>
<span id="L313" rel="#L313">313</span>
<span id="L314" rel="#L314">314</span>
<span id="L315" rel="#L315">315</span>
<span id="L316" rel="#L316">316</span>
<span id="L317" rel="#L317">317</span>
<span id="L318" rel="#L318">318</span>
<span id="L319" rel="#L319">319</span>
<span id="L320" rel="#L320">320</span>
<span id="L321" rel="#L321">321</span>
<span id="L322" rel="#L322">322</span>
<span id="L323" rel="#L323">323</span>
<span id="L324" rel="#L324">324</span>
<span id="L325" rel="#L325">325</span>
<span id="L326" rel="#L326">326</span>
<span id="L327" rel="#L327">327</span>
<span id="L328" rel="#L328">328</span>
<span id="L329" rel="#L329">329</span>
<span id="L330" rel="#L330">330</span>
<span id="L331" rel="#L331">331</span>
<span id="L332" rel="#L332">332</span>
<span id="L333" rel="#L333">333</span>
<span id="L334" rel="#L334">334</span>
<span id="L335" rel="#L335">335</span>
<span id="L336" rel="#L336">336</span>
<span id="L337" rel="#L337">337</span>
<span id="L338" rel="#L338">338</span>
<span id="L339" rel="#L339">339</span>
<span id="L340" rel="#L340">340</span>
<span id="L341" rel="#L341">341</span>
<span id="L342" rel="#L342">342</span>
<span id="L343" rel="#L343">343</span>
<span id="L344" rel="#L344">344</span>
<span id="L345" rel="#L345">345</span>
<span id="L346" rel="#L346">346</span>
<span id="L347" rel="#L347">347</span>
<span id="L348" rel="#L348">348</span>
<span id="L349" rel="#L349">349</span>
<span id="L350" rel="#L350">350</span>
<span id="L351" rel="#L351">351</span>
<span id="L352" rel="#L352">352</span>
<span id="L353" rel="#L353">353</span>
<span id="L354" rel="#L354">354</span>
<span id="L355" rel="#L355">355</span>
<span id="L356" rel="#L356">356</span>
<span id="L357" rel="#L357">357</span>
<span id="L358" rel="#L358">358</span>
<span id="L359" rel="#L359">359</span>
<span id="L360" rel="#L360">360</span>
<span id="L361" rel="#L361">361</span>
<span id="L362" rel="#L362">362</span>
<span id="L363" rel="#L363">363</span>
<span id="L364" rel="#L364">364</span>
<span id="L365" rel="#L365">365</span>
<span id="L366" rel="#L366">366</span>
<span id="L367" rel="#L367">367</span>
<span id="L368" rel="#L368">368</span>
<span id="L369" rel="#L369">369</span>
<span id="L370" rel="#L370">370</span>
<span id="L371" rel="#L371">371</span>
<span id="L372" rel="#L372">372</span>
<span id="L373" rel="#L373">373</span>
<span id="L374" rel="#L374">374</span>
<span id="L375" rel="#L375">375</span>
<span id="L376" rel="#L376">376</span>
<span id="L377" rel="#L377">377</span>
<span id="L378" rel="#L378">378</span>
<span id="L379" rel="#L379">379</span>
<span id="L380" rel="#L380">380</span>
<span id="L381" rel="#L381">381</span>
<span id="L382" rel="#L382">382</span>
<span id="L383" rel="#L383">383</span>
<span id="L384" rel="#L384">384</span>
<span id="L385" rel="#L385">385</span>
<span id="L386" rel="#L386">386</span>
<span id="L387" rel="#L387">387</span>
<span id="L388" rel="#L388">388</span>
<span id="L389" rel="#L389">389</span>
<span id="L390" rel="#L390">390</span>
<span id="L391" rel="#L391">391</span>
<span id="L392" rel="#L392">392</span>
<span id="L393" rel="#L393">393</span>
<span id="L394" rel="#L394">394</span>
<span id="L395" rel="#L395">395</span>
<span id="L396" rel="#L396">396</span>
<span id="L397" rel="#L397">397</span>
<span id="L398" rel="#L398">398</span>
<span id="L399" rel="#L399">399</span>
<span id="L400" rel="#L400">400</span>
<span id="L401" rel="#L401">401</span>
<span id="L402" rel="#L402">402</span>
<span id="L403" rel="#L403">403</span>
<span id="L404" rel="#L404">404</span>
<span id="L405" rel="#L405">405</span>
<span id="L406" rel="#L406">406</span>
<span id="L407" rel="#L407">407</span>
<span id="L408" rel="#L408">408</span>
<span id="L409" rel="#L409">409</span>
<span id="L410" rel="#L410">410</span>
<span id="L411" rel="#L411">411</span>
<span id="L412" rel="#L412">412</span>
<span id="L413" rel="#L413">413</span>
<span id="L414" rel="#L414">414</span>
<span id="L415" rel="#L415">415</span>
<span id="L416" rel="#L416">416</span>
<span id="L417" rel="#L417">417</span>
<span id="L418" rel="#L418">418</span>
<span id="L419" rel="#L419">419</span>
<span id="L420" rel="#L420">420</span>
<span id="L421" rel="#L421">421</span>
<span id="L422" rel="#L422">422</span>
<span id="L423" rel="#L423">423</span>
<span id="L424" rel="#L424">424</span>
<span id="L425" rel="#L425">425</span>
<span id="L426" rel="#L426">426</span>
<span id="L427" rel="#L427">427</span>
<span id="L428" rel="#L428">428</span>
<span id="L429" rel="#L429">429</span>
<span id="L430" rel="#L430">430</span>
<span id="L431" rel="#L431">431</span>
<span id="L432" rel="#L432">432</span>
<span id="L433" rel="#L433">433</span>
<span id="L434" rel="#L434">434</span>
<span id="L435" rel="#L435">435</span>
<span id="L436" rel="#L436">436</span>
<span id="L437" rel="#L437">437</span>
<span id="L438" rel="#L438">438</span>
<span id="L439" rel="#L439">439</span>
<span id="L440" rel="#L440">440</span>
<span id="L441" rel="#L441">441</span>
<span id="L442" rel="#L442">442</span>
<span id="L443" rel="#L443">443</span>
<span id="L444" rel="#L444">444</span>
<span id="L445" rel="#L445">445</span>
<span id="L446" rel="#L446">446</span>
<span id="L447" rel="#L447">447</span>
<span id="L448" rel="#L448">448</span>
<span id="L449" rel="#L449">449</span>
<span id="L450" rel="#L450">450</span>
<span id="L451" rel="#L451">451</span>
<span id="L452" rel="#L452">452</span>
<span id="L453" rel="#L453">453</span>
<span id="L454" rel="#L454">454</span>
<span id="L455" rel="#L455">455</span>
<span id="L456" rel="#L456">456</span>
<span id="L457" rel="#L457">457</span>
<span id="L458" rel="#L458">458</span>
<span id="L459" rel="#L459">459</span>
<span id="L460" rel="#L460">460</span>
<span id="L461" rel="#L461">461</span>
<span id="L462" rel="#L462">462</span>
<span id="L463" rel="#L463">463</span>
<span id="L464" rel="#L464">464</span>
<span id="L465" rel="#L465">465</span>
<span id="L466" rel="#L466">466</span>
<span id="L467" rel="#L467">467</span>
<span id="L468" rel="#L468">468</span>
<span id="L469" rel="#L469">469</span>
<span id="L470" rel="#L470">470</span>
<span id="L471" rel="#L471">471</span>
<span id="L472" rel="#L472">472</span>
<span id="L473" rel="#L473">473</span>
<span id="L474" rel="#L474">474</span>
<span id="L475" rel="#L475">475</span>
<span id="L476" rel="#L476">476</span>
<span id="L477" rel="#L477">477</span>
<span id="L478" rel="#L478">478</span>
<span id="L479" rel="#L479">479</span>
<span id="L480" rel="#L480">480</span>
<span id="L481" rel="#L481">481</span>
<span id="L482" rel="#L482">482</span>
<span id="L483" rel="#L483">483</span>
<span id="L484" rel="#L484">484</span>
<span id="L485" rel="#L485">485</span>
<span id="L486" rel="#L486">486</span>
<span id="L487" rel="#L487">487</span>
<span id="L488" rel="#L488">488</span>
<span id="L489" rel="#L489">489</span>
<span id="L490" rel="#L490">490</span>
<span id="L491" rel="#L491">491</span>
<span id="L492" rel="#L492">492</span>
<span id="L493" rel="#L493">493</span>
<span id="L494" rel="#L494">494</span>
<span id="L495" rel="#L495">495</span>
<span id="L496" rel="#L496">496</span>
<span id="L497" rel="#L497">497</span>
<span id="L498" rel="#L498">498</span>
<span id="L499" rel="#L499">499</span>
<span id="L500" rel="#L500">500</span>
<span id="L501" rel="#L501">501</span>
<span id="L502" rel="#L502">502</span>
<span id="L503" rel="#L503">503</span>
<span id="L504" rel="#L504">504</span>
<span id="L505" rel="#L505">505</span>
<span id="L506" rel="#L506">506</span>
<span id="L507" rel="#L507">507</span>
<span id="L508" rel="#L508">508</span>
<span id="L509" rel="#L509">509</span>
<span id="L510" rel="#L510">510</span>
<span id="L511" rel="#L511">511</span>
<span id="L512" rel="#L512">512</span>
<span id="L513" rel="#L513">513</span>
<span id="L514" rel="#L514">514</span>
<span id="L515" rel="#L515">515</span>
<span id="L516" rel="#L516">516</span>
<span id="L517" rel="#L517">517</span>
<span id="L518" rel="#L518">518</span>
<span id="L519" rel="#L519">519</span>
<span id="L520" rel="#L520">520</span>
<span id="L521" rel="#L521">521</span>
<span id="L522" rel="#L522">522</span>
<span id="L523" rel="#L523">523</span>
<span id="L524" rel="#L524">524</span>
<span id="L525" rel="#L525">525</span>
</pre>
          </td>
          <td width="100%">
                <div class="highlight"><pre><div class='line' id='LC1'><span class="cm">/**</span></div><div class='line' id='LC2'><span class="cm">* XMLHttpRequest.js Copyright (C) 2011 Sergey Ilinsky (http://www.ilinsky.com)</span></div><div class='line' id='LC3'><span class="cm">*</span></div><div class='line' id='LC4'><span class="cm">* This work is free software; you can redistribute it and/or modify</span></div><div class='line' id='LC5'><span class="cm">* it under the terms of the GNU Lesser General Public License as published by</span></div><div class='line' id='LC6'><span class="cm">* the Free Software Foundation; either version 2.1 of the License, or</span></div><div class='line' id='LC7'><span class="cm">* (at your option) any later version.</span></div><div class='line' id='LC8'><span class="cm">*</span></div><div class='line' id='LC9'><span class="cm">* This work is distributed in the hope that it will be useful,</span></div><div class='line' id='LC10'><span class="cm">* but without any warranty; without even the implied warranty of</span></div><div class='line' id='LC11'><span class="cm">* merchantability or fitness for a particular purpose. See the</span></div><div class='line' id='LC12'><span class="cm">* GNU Lesser General Public License for more details.</span></div><div class='line' id='LC13'><span class="cm">*</span></div><div class='line' id='LC14'><span class="cm">* You should have received a copy of the GNU Lesser General Public License</span></div><div class='line' id='LC15'><span class="cm">* along with this library; if not, write to the Free Software Foundation, Inc.,</span></div><div class='line' id='LC16'><span class="cm">* 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA</span></div><div class='line' id='LC17'><span class="cm">*/</span></div><div class='line' id='LC18'><br/></div><div class='line' id='LC19'><span class="p">(</span><span class="kd">function</span> <span class="p">()</span> <span class="p">{</span></div><div class='line' id='LC20'><br/></div><div class='line' id='LC21'>	<span class="c1">// Save reference to earlier defined object implementation (if any)</span></div><div class='line' id='LC22'>	<span class="kd">var</span> <span class="nx">oXMLHttpRequest</span> <span class="o">=</span> <span class="nb">window</span><span class="p">.</span><span class="nx">XMLHttpRequest</span><span class="p">;</span></div><div class='line' id='LC23'><br/></div><div class='line' id='LC24'>	<span class="c1">// Define on browser type</span></div><div class='line' id='LC25'>	<span class="kd">var</span> <span class="nx">bGecko</span>  <span class="o">=</span> <span class="o">!!</span><span class="nb">window</span><span class="p">.</span><span class="nx">controllers</span><span class="p">;</span></div><div class='line' id='LC26'>	<span class="kd">var</span> <span class="nx">bIE</span>     <span class="o">=</span> <span class="nb">window</span><span class="p">.</span><span class="nb">document</span><span class="p">.</span><span class="nx">all</span> <span class="o">&amp;&amp;</span> <span class="o">!</span><span class="nb">window</span><span class="p">.</span><span class="nx">opera</span><span class="p">;</span></div><div class='line' id='LC27'>	<span class="kd">var</span> <span class="nx">bIE7</span>    <span class="o">=</span> <span class="nx">bIE</span> <span class="o">&amp;&amp;</span> <span class="nb">window</span><span class="p">.</span><span class="nx">navigator</span><span class="p">.</span><span class="nx">userAgent</span><span class="p">.</span><span class="nx">match</span><span class="p">(</span><span class="sr">/MSIE 7.0/</span><span class="p">);</span></div><div class='line' id='LC28'><br/></div><div class='line' id='LC29'>	<span class="c1">// Enables &quot;XMLHttpRequest()&quot; call next to &quot;new XMLHttpRequest()&quot;</span></div><div class='line' id='LC30'>	<span class="kd">function</span> <span class="nx">fXMLHttpRequest</span><span class="p">()</span> <span class="p">{</span></div><div class='line' id='LC31'>		<span class="k">this</span><span class="p">.</span><span class="nx">_object</span>  <span class="o">=</span> <span class="nx">oXMLHttpRequest</span> <span class="o">&amp;&amp;</span> <span class="o">!</span><span class="nx">bIE7</span> <span class="o">?</span> <span class="k">new</span> <span class="nx">oXMLHttpRequest</span> <span class="o">:</span> <span class="k">new</span> <span class="nb">window</span><span class="p">.</span><span class="nx">ActiveXObject</span><span class="p">(</span><span class="s2">&quot;Microsoft.XMLHTTP&quot;</span><span class="p">);</span></div><div class='line' id='LC32'>		<span class="k">this</span><span class="p">.</span><span class="nx">_listeners</span> <span class="o">=</span> <span class="p">[];</span></div><div class='line' id='LC33'>	<span class="p">}</span></div><div class='line' id='LC34'><br/></div><div class='line' id='LC35'>	<span class="c1">// Constructor</span></div><div class='line' id='LC36'>	<span class="kd">function</span> <span class="nx">cXMLHttpRequest</span><span class="p">()</span> <span class="p">{</span></div><div class='line' id='LC37'>		<span class="k">return</span> <span class="k">new</span> <span class="nx">fXMLHttpRequest</span><span class="p">;</span></div><div class='line' id='LC38'>	<span class="p">}</span></div><div class='line' id='LC39'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span> <span class="o">=</span> <span class="nx">fXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">;</span></div><div class='line' id='LC40'><br/></div><div class='line' id='LC41'>	<span class="c1">// BUGFIX: Firefox with Firebug installed would break pages if not executed</span></div><div class='line' id='LC42'>	<span class="k">if</span> <span class="p">(</span><span class="nx">bGecko</span> <span class="o">&amp;&amp;</span> <span class="nx">oXMLHttpRequest</span><span class="p">.</span><span class="nx">wrapped</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC43'>		<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">wrapped</span> <span class="o">=</span> <span class="nx">oXMLHttpRequest</span><span class="p">.</span><span class="nx">wrapped</span><span class="p">;</span></div><div class='line' id='LC44'>	<span class="p">}</span></div><div class='line' id='LC45'><br/></div><div class='line' id='LC46'>	<span class="c1">// Constants</span></div><div class='line' id='LC47'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">UNSENT</span>            <span class="o">=</span> <span class="mi">0</span><span class="p">;</span></div><div class='line' id='LC48'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">OPENED</span>            <span class="o">=</span> <span class="mi">1</span><span class="p">;</span></div><div class='line' id='LC49'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">HEADERS_RECEIVED</span>  <span class="o">=</span> <span class="mi">2</span><span class="p">;</span></div><div class='line' id='LC50'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">LOADING</span>           <span class="o">=</span> <span class="mi">3</span><span class="p">;</span></div><div class='line' id='LC51'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">DONE</span>              <span class="o">=</span> <span class="mi">4</span><span class="p">;</span></div><div class='line' id='LC52'><br/></div><div class='line' id='LC53'>	<span class="c1">// Interface level constants</span></div><div class='line' id='LC54'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">UNSENT</span>            <span class="o">=</span> <span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">UNSENT</span><span class="p">;</span></div><div class='line' id='LC55'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">OPENED</span>            <span class="o">=</span> <span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">OPENED</span><span class="p">;</span></div><div class='line' id='LC56'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">HEADERS_RECEIVED</span>  <span class="o">=</span> <span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">HEADERS_RECEIVED</span><span class="p">;</span></div><div class='line' id='LC57'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">LOADING</span>           <span class="o">=</span> <span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">LOADING</span><span class="p">;</span></div><div class='line' id='LC58'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">DONE</span>              <span class="o">=</span> <span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">DONE</span><span class="p">;</span></div><div class='line' id='LC59'><br/></div><div class='line' id='LC60'>	<span class="c1">// Public Properties</span></div><div class='line' id='LC61'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">readyState</span>    <span class="o">=</span> <span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">UNSENT</span><span class="p">;</span></div><div class='line' id='LC62'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">responseText</span>  <span class="o">=</span> <span class="s1">&#39;&#39;</span><span class="p">;</span></div><div class='line' id='LC63'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">responseXML</span>   <span class="o">=</span> <span class="kc">null</span><span class="p">;</span></div><div class='line' id='LC64'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">status</span>        <span class="o">=</span> <span class="mi">0</span><span class="p">;</span></div><div class='line' id='LC65'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">statusText</span>    <span class="o">=</span> <span class="s1">&#39;&#39;</span><span class="p">;</span></div><div class='line' id='LC66'><br/></div><div class='line' id='LC67'>	<span class="c1">// Priority proposal</span></div><div class='line' id='LC68'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">priority</span>    <span class="o">=</span> <span class="s2">&quot;NORMAL&quot;</span><span class="p">;</span></div><div class='line' id='LC69'><br/></div><div class='line' id='LC70'>	<span class="c1">// Instance-level Events Handlers</span></div><div class='line' id='LC71'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">onreadystatechange</span>  <span class="o">=</span> <span class="kc">null</span><span class="p">;</span></div><div class='line' id='LC72'><br/></div><div class='line' id='LC73'>	<span class="c1">// Class-level Events Handlers</span></div><div class='line' id='LC74'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">onreadystatechange</span>  <span class="o">=</span> <span class="kc">null</span><span class="p">;</span></div><div class='line' id='LC75'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">onopen</span>              <span class="o">=</span> <span class="kc">null</span><span class="p">;</span></div><div class='line' id='LC76'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">onsend</span>              <span class="o">=</span> <span class="kc">null</span><span class="p">;</span></div><div class='line' id='LC77'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">onabort</span>             <span class="o">=</span> <span class="kc">null</span><span class="p">;</span></div><div class='line' id='LC78'><br/></div><div class='line' id='LC79'>	<span class="c1">// Public Methods</span></div><div class='line' id='LC80'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">open</span>  <span class="o">=</span> <span class="kd">function</span><span class="p">(</span><span class="nx">sMethod</span><span class="p">,</span> <span class="nx">sUrl</span><span class="p">,</span> <span class="nx">bAsync</span><span class="p">,</span> <span class="nx">sUser</span><span class="p">,</span> <span class="nx">sPassword</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC81'>		<span class="c1">// http://www.w3.org/TR/XMLHttpRequest/#the-open-method</span></div><div class='line' id='LC82'>		<span class="kd">var</span> <span class="nx">backlist</span> <span class="o">=</span> <span class="nx">sMethod</span><span class="p">.</span><span class="nx">toLowerCase</span><span class="p">();</span></div><div class='line' id='LC83'>		<span class="k">if</span><span class="p">((</span><span class="nx">backlist</span> <span class="o">==</span> <span class="s2">&quot;connect&quot;</span><span class="p">)</span> <span class="o">||</span> <span class="p">(</span><span class="nx">backlist</span> <span class="o">==</span> <span class="s2">&quot;trace&quot;</span><span class="p">)</span> <span class="o">||</span> <span class="p">(</span><span class="nx">backlist</span> <span class="o">==</span> <span class="s2">&quot;track&quot;</span><span class="p">)){</span></div><div class='line' id='LC84'>			<span class="c1">// Using a generic error and an int - not too sure all browsers support correctly</span></div><div class='line' id='LC85'>			<span class="c1">// http://dvcs.w3.org/hg/domcore/raw-file/tip/Overview.html#securityerror, so, this is safer</span></div><div class='line' id='LC86'>			<span class="c1">// XXX should do better than that, but this is OT to XHR.</span></div><div class='line' id='LC87'>			<span class="k">throw</span> <span class="k">new</span> <span class="nb">Error</span><span class="p">(</span><span class="mi">18</span><span class="p">);</span></div><div class='line' id='LC88'>		<span class="p">}</span></div><div class='line' id='LC89'><br/></div><div class='line' id='LC90'>		<span class="c1">// Delete headers, required when object is reused</span></div><div class='line' id='LC91'>		<span class="k">delete</span> <span class="k">this</span><span class="p">.</span><span class="nx">_headers</span><span class="p">;</span></div><div class='line' id='LC92'><br/></div><div class='line' id='LC93'>		<span class="c1">// When bAsync parameter value is omitted, use true as default</span></div><div class='line' id='LC94'>		<span class="k">if</span> <span class="p">(</span><span class="nx">arguments</span><span class="p">.</span><span class="nx">length</span> <span class="o">&lt;</span> <span class="mi">3</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC95'>			<span class="nx">bAsync</span>  <span class="o">=</span> <span class="kc">true</span><span class="p">;</span></div><div class='line' id='LC96'>		<span class="p">}</span></div><div class='line' id='LC97'><br/></div><div class='line' id='LC98'>		<span class="c1">// Save async parameter for fixing Gecko bug with missing readystatechange in synchronous requests</span></div><div class='line' id='LC99'>		<span class="k">this</span><span class="p">.</span><span class="nx">_async</span>   <span class="o">=</span> <span class="nx">bAsync</span><span class="p">;</span></div><div class='line' id='LC100'><br/></div><div class='line' id='LC101'>		<span class="c1">// Set the onreadystatechange handler</span></div><div class='line' id='LC102'>		<span class="kd">var</span> <span class="nx">oRequest</span>  <span class="o">=</span> <span class="k">this</span><span class="p">;</span></div><div class='line' id='LC103'>		<span class="kd">var</span> <span class="nx">nState</span>    <span class="o">=</span> <span class="k">this</span><span class="p">.</span><span class="nx">readyState</span><span class="p">;</span></div><div class='line' id='LC104'>		<span class="kd">var</span> <span class="nx">fOnUnload</span> <span class="o">=</span> <span class="kc">null</span><span class="p">;</span></div><div class='line' id='LC105'><br/></div><div class='line' id='LC106'>		<span class="c1">// BUGFIX: IE - memory leak on page unload (inter-page leak)</span></div><div class='line' id='LC107'>		<span class="k">if</span> <span class="p">(</span><span class="nx">bIE</span> <span class="o">&amp;&amp;</span> <span class="nx">bAsync</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC108'>			<span class="nx">fOnUnload</span> <span class="o">=</span> <span class="kd">function</span><span class="p">()</span> <span class="p">{</span></div><div class='line' id='LC109'>				<span class="k">if</span> <span class="p">(</span><span class="nx">nState</span> <span class="o">!=</span> <span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">DONE</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC110'>					<span class="nx">fCleanTransport</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">);</span></div><div class='line' id='LC111'>					<span class="c1">// Safe to abort here since onreadystatechange handler removed</span></div><div class='line' id='LC112'>					<span class="nx">oRequest</span><span class="p">.</span><span class="nx">abort</span><span class="p">();</span></div><div class='line' id='LC113'>				<span class="p">}</span></div><div class='line' id='LC114'>			<span class="p">};</span></div><div class='line' id='LC115'>			<span class="nb">window</span><span class="p">.</span><span class="nx">attachEvent</span><span class="p">(</span><span class="s2">&quot;onunload&quot;</span><span class="p">,</span> <span class="nx">fOnUnload</span><span class="p">);</span></div><div class='line' id='LC116'>		<span class="p">}</span></div><div class='line' id='LC117'><br/></div><div class='line' id='LC118'>		<span class="c1">// Add method sniffer</span></div><div class='line' id='LC119'>		<span class="k">if</span> <span class="p">(</span><span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">onopen</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC120'>			<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">onopen</span><span class="p">.</span><span class="nx">apply</span><span class="p">(</span><span class="k">this</span><span class="p">,</span> <span class="nx">arguments</span><span class="p">);</span></div><div class='line' id='LC121'>		<span class="p">}</span></div><div class='line' id='LC122'><br/></div><div class='line' id='LC123'>		<span class="k">if</span> <span class="p">(</span><span class="nx">arguments</span><span class="p">.</span><span class="nx">length</span> <span class="o">&gt;</span> <span class="mi">4</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC124'>			<span class="k">this</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">open</span><span class="p">(</span><span class="nx">sMethod</span><span class="p">,</span> <span class="nx">sUrl</span><span class="p">,</span> <span class="nx">bAsync</span><span class="p">,</span> <span class="nx">sUser</span><span class="p">,</span> <span class="nx">sPassword</span><span class="p">);</span></div><div class='line' id='LC125'>		<span class="p">}</span> <span class="k">else</span> <span class="k">if</span> <span class="p">(</span><span class="nx">arguments</span><span class="p">.</span><span class="nx">length</span> <span class="o">&gt;</span> <span class="mi">3</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC126'>			<span class="k">this</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">open</span><span class="p">(</span><span class="nx">sMethod</span><span class="p">,</span> <span class="nx">sUrl</span><span class="p">,</span> <span class="nx">bAsync</span><span class="p">,</span> <span class="nx">sUser</span><span class="p">);</span></div><div class='line' id='LC127'>		<span class="p">}</span> <span class="k">else</span> <span class="p">{</span></div><div class='line' id='LC128'>			<span class="k">this</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">open</span><span class="p">(</span><span class="nx">sMethod</span><span class="p">,</span> <span class="nx">sUrl</span><span class="p">,</span> <span class="nx">bAsync</span><span class="p">);</span></div><div class='line' id='LC129'>		<span class="p">}</span></div><div class='line' id='LC130'><br/></div><div class='line' id='LC131'>		<span class="k">this</span><span class="p">.</span><span class="nx">readyState</span> <span class="o">=</span> <span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">OPENED</span><span class="p">;</span></div><div class='line' id='LC132'>		<span class="nx">fReadyStateChange</span><span class="p">(</span><span class="k">this</span><span class="p">);</span></div><div class='line' id='LC133'><br/></div><div class='line' id='LC134'>		<span class="k">this</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">onreadystatechange</span> <span class="o">=</span> <span class="kd">function</span><span class="p">()</span> <span class="p">{</span></div><div class='line' id='LC135'>			<span class="k">if</span> <span class="p">(</span><span class="nx">bGecko</span> <span class="o">&amp;&amp;</span> <span class="o">!</span><span class="nx">bAsync</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC136'>				<span class="k">return</span><span class="p">;</span></div><div class='line' id='LC137'>			<span class="p">}</span></div><div class='line' id='LC138'><br/></div><div class='line' id='LC139'>			<span class="c1">// Synchronize state</span></div><div class='line' id='LC140'>			<span class="nx">oRequest</span><span class="p">.</span><span class="nx">readyState</span>   <span class="o">=</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">readyState</span><span class="p">;</span></div><div class='line' id='LC141'>			<span class="nx">fSynchronizeValues</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">);</span></div><div class='line' id='LC142'><br/></div><div class='line' id='LC143'>			<span class="c1">// BUGFIX: Firefox fires unnecessary DONE when aborting</span></div><div class='line' id='LC144'>			<span class="k">if</span> <span class="p">(</span><span class="nx">oRequest</span><span class="p">.</span><span class="nx">_aborted</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC145'>				<span class="c1">// Reset readyState to UNSENT</span></div><div class='line' id='LC146'>				<span class="nx">oRequest</span><span class="p">.</span><span class="nx">readyState</span> <span class="o">=</span> <span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">UNSENT</span><span class="p">;</span></div><div class='line' id='LC147'><br/></div><div class='line' id='LC148'>				<span class="c1">// Return now</span></div><div class='line' id='LC149'>				<span class="k">return</span><span class="p">;</span></div><div class='line' id='LC150'>			<span class="p">}</span></div><div class='line' id='LC151'><br/></div><div class='line' id='LC152'>			<span class="k">if</span> <span class="p">(</span><span class="nx">oRequest</span><span class="p">.</span><span class="nx">readyState</span> <span class="o">==</span> <span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">DONE</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC153'>				<span class="c1">// Free up queue</span></div><div class='line' id='LC154'>				<span class="k">delete</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">_data</span><span class="p">;</span></div><div class='line' id='LC155'><br/></div><div class='line' id='LC156'>				<span class="c1">// Uncomment these lines for bAsync</span></div><div class='line' id='LC157'>				<span class="cm">/**</span></div><div class='line' id='LC158'><span class="cm">				 * if (bAsync) {</span></div><div class='line' id='LC159'><span class="cm">				 * 	fQueue_remove(oRequest);</span></div><div class='line' id='LC160'><span class="cm">				 * }</span></div><div class='line' id='LC161'><span class="cm">				 */</span></div><div class='line' id='LC162'><br/></div><div class='line' id='LC163'>				<span class="nx">fCleanTransport</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">);</span></div><div class='line' id='LC164'><br/></div><div class='line' id='LC165'>				<span class="c1">// Uncomment this block if you need a fix for IE cache</span></div><div class='line' id='LC166'>				<span class="cm">/**</span></div><div class='line' id='LC167'><span class="cm">				 * // BUGFIX: IE - cache issue</span></div><div class='line' id='LC168'><span class="cm">				 * if (!oRequest._object.getResponseHeader(&quot;Date&quot;)) {</span></div><div class='line' id='LC169'><span class="cm">				 * 	// Save object to cache</span></div><div class='line' id='LC170'><span class="cm">				 * 	oRequest._cached  = oRequest._object;</span></div><div class='line' id='LC171'><span class="cm">				 *</span></div><div class='line' id='LC172'><span class="cm">				 * 	// Instantiate a new transport object</span></div><div class='line' id='LC173'><span class="cm">				 * 	cXMLHttpRequest.call(oRequest);</span></div><div class='line' id='LC174'><span class="cm">				 *</span></div><div class='line' id='LC175'><span class="cm">				 * 	// Re-send request</span></div><div class='line' id='LC176'><span class="cm">				 * 	if (sUser) {</span></div><div class='line' id='LC177'><span class="cm">				 * 		if (sPassword) {</span></div><div class='line' id='LC178'><span class="cm">				 * 			oRequest._object.open(sMethod, sUrl, bAsync, sUser, sPassword);</span></div><div class='line' id='LC179'><span class="cm">				 * 		} else {</span></div><div class='line' id='LC180'><span class="cm">				 * 			oRequest._object.open(sMethod, sUrl, bAsync);</span></div><div class='line' id='LC181'><span class="cm">				 * 		}</span></div><div class='line' id='LC182'><span class="cm">				 *</span></div><div class='line' id='LC183'><span class="cm">				 * 		oRequest._object.setRequestHeader(&quot;If-Modified-Since&quot;, oRequest._cached.getResponseHeader(&quot;Last-Modified&quot;) || new window.Date(0));</span></div><div class='line' id='LC184'><span class="cm">				 * 		// Copy headers set</span></div><div class='line' id='LC185'><span class="cm">				 * 		if (oRequest._headers) {</span></div><div class='line' id='LC186'><span class="cm">				 * 			for (var sHeader in oRequest._headers) {</span></div><div class='line' id='LC187'><span class="cm">				 * 				// Some frameworks prototype objects with functions</span></div><div class='line' id='LC188'><span class="cm">				 * 				if (typeof oRequest._headers[sHeader] == &quot;string&quot;) {</span></div><div class='line' id='LC189'><span class="cm">				 * 					oRequest._object.setRequestHeader(sHeader, oRequest._headers[sHeader]);</span></div><div class='line' id='LC190'><span class="cm">				 * 				}</span></div><div class='line' id='LC191'><span class="cm">				 * 			}</span></div><div class='line' id='LC192'><span class="cm">				 * 		}</span></div><div class='line' id='LC193'><span class="cm">				 * 		oRequest._object.onreadystatechange = function() {</span></div><div class='line' id='LC194'><span class="cm">				 * 			// Synchronize state</span></div><div class='line' id='LC195'><span class="cm">				 * 			oRequest.readyState   = oRequest._object.readyState;</span></div><div class='line' id='LC196'><span class="cm">				 *</span></div><div class='line' id='LC197'><span class="cm">				 * 			if (oRequest._aborted) {</span></div><div class='line' id='LC198'><span class="cm">				 * 				//</span></div><div class='line' id='LC199'><span class="cm">				 * 				oRequest.readyState = cXMLHttpRequest.UNSENT;</span></div><div class='line' id='LC200'><span class="cm">				 *</span></div><div class='line' id='LC201'><span class="cm">				 * 				// Return</span></div><div class='line' id='LC202'><span class="cm">				 * 				return;</span></div><div class='line' id='LC203'><span class="cm">				 * 			}</span></div><div class='line' id='LC204'><span class="cm">				 *</span></div><div class='line' id='LC205'><span class="cm">				 * 			if (oRequest.readyState == cXMLHttpRequest.DONE) {</span></div><div class='line' id='LC206'><span class="cm">				 * 				// Clean Object</span></div><div class='line' id='LC207'><span class="cm">				 * 				fCleanTransport(oRequest);</span></div><div class='line' id='LC208'><span class="cm">				 *</span></div><div class='line' id='LC209'><span class="cm">				 * 				// get cached request</span></div><div class='line' id='LC210'><span class="cm">				 * 				if (oRequest.status == 304) {</span></div><div class='line' id='LC211'><span class="cm">				 * 					oRequest._object  = oRequest._cached;</span></div><div class='line' id='LC212'><span class="cm">				 * 				}</span></div><div class='line' id='LC213'><span class="cm">				 *</span></div><div class='line' id='LC214'><span class="cm">				 * 				//</span></div><div class='line' id='LC215'><span class="cm">				 * 				delete oRequest._cached;</span></div><div class='line' id='LC216'><span class="cm">				 *</span></div><div class='line' id='LC217'><span class="cm">				 * 				//</span></div><div class='line' id='LC218'><span class="cm">				 * 				fSynchronizeValues(oRequest);</span></div><div class='line' id='LC219'><span class="cm">				 *</span></div><div class='line' id='LC220'><span class="cm">				 * 				//</span></div><div class='line' id='LC221'><span class="cm">				 * 				fReadyStateChange(oRequest);</span></div><div class='line' id='LC222'><span class="cm">				 *</span></div><div class='line' id='LC223'><span class="cm">				 * 				// BUGFIX: IE - memory leak in interrupted</span></div><div class='line' id='LC224'><span class="cm">				 * 				if (bIE &amp;&amp; bAsync) {</span></div><div class='line' id='LC225'><span class="cm">				 * 					window.detachEvent(&quot;onunload&quot;, fOnUnload);</span></div><div class='line' id='LC226'><span class="cm">				 * 				}</span></div><div class='line' id='LC227'><span class="cm">				 *</span></div><div class='line' id='LC228'><span class="cm">				 * 			}</span></div><div class='line' id='LC229'><span class="cm">				 * 		};</span></div><div class='line' id='LC230'><span class="cm">				 * 		oRequest._object.send(null);</span></div><div class='line' id='LC231'><span class="cm">				 *</span></div><div class='line' id='LC232'><span class="cm">				 * 		// Return now - wait until re-sent request is finished</span></div><div class='line' id='LC233'><span class="cm">				 * 		return;</span></div><div class='line' id='LC234'><span class="cm">				 * 	};</span></div><div class='line' id='LC235'><span class="cm">				 */</span></div><div class='line' id='LC236'><br/></div><div class='line' id='LC237'>				<span class="c1">// BUGFIX: IE - memory leak in interrupted</span></div><div class='line' id='LC238'>				<span class="k">if</span> <span class="p">(</span><span class="nx">bIE</span> <span class="o">&amp;&amp;</span> <span class="nx">bAsync</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC239'>					<span class="nb">window</span><span class="p">.</span><span class="nx">detachEvent</span><span class="p">(</span><span class="s2">&quot;onunload&quot;</span><span class="p">,</span> <span class="nx">fOnUnload</span><span class="p">);</span></div><div class='line' id='LC240'>				<span class="p">}</span></div><div class='line' id='LC241'><br/></div><div class='line' id='LC242'>				<span class="c1">// BUGFIX: Some browsers (Internet Explorer, Gecko) fire OPEN readystate twice</span></div><div class='line' id='LC243'>				<span class="k">if</span> <span class="p">(</span><span class="nx">nState</span> <span class="o">!=</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">readyState</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC244'>					<span class="nx">fReadyStateChange</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">);</span></div><div class='line' id='LC245'>				<span class="p">}</span></div><div class='line' id='LC246'><br/></div><div class='line' id='LC247'>				<span class="nx">nState</span>  <span class="o">=</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">readyState</span><span class="p">;</span></div><div class='line' id='LC248'>			<span class="p">}</span></div><div class='line' id='LC249'>		<span class="p">};</span></div><div class='line' id='LC250'>	<span class="p">};</span></div><div class='line' id='LC251'><br/></div><div class='line' id='LC252'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">send</span> <span class="o">=</span> <span class="kd">function</span><span class="p">(</span><span class="nx">vData</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC253'>		<span class="c1">// Add method sniffer</span></div><div class='line' id='LC254'>		<span class="k">if</span> <span class="p">(</span><span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">onsend</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC255'>			<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">onsend</span><span class="p">.</span><span class="nx">apply</span><span class="p">(</span><span class="k">this</span><span class="p">,</span> <span class="nx">arguments</span><span class="p">);</span></div><div class='line' id='LC256'>		<span class="p">}</span></div><div class='line' id='LC257'><br/></div><div class='line' id='LC258'>		<span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="nx">arguments</span><span class="p">.</span><span class="nx">length</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC259'>			<span class="nx">vData</span> <span class="o">=</span> <span class="kc">null</span><span class="p">;</span></div><div class='line' id='LC260'>		<span class="p">}</span></div><div class='line' id='LC261'><br/></div><div class='line' id='LC262'>		<span class="c1">// BUGFIX: Safari - fails sending documents created/modified dynamically, so an explicit serialization required</span></div><div class='line' id='LC263'>		<span class="c1">// BUGFIX: IE - rewrites any custom mime-type to &quot;text/xml&quot; in case an XMLNode is sent</span></div><div class='line' id='LC264'>		<span class="c1">// BUGFIX: Gecko - fails sending Element (this is up to the implementation either to standard)</span></div><div class='line' id='LC265'>		<span class="k">if</span> <span class="p">(</span><span class="nx">vData</span> <span class="o">&amp;&amp;</span> <span class="nx">vData</span><span class="p">.</span><span class="nx">nodeType</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC266'>			<span class="nx">vData</span> <span class="o">=</span> <span class="nb">window</span><span class="p">.</span><span class="nx">XMLSerializer</span> <span class="o">?</span> <span class="k">new</span> <span class="nb">window</span><span class="p">.</span><span class="nx">XMLSerializer</span><span class="p">().</span><span class="nx">serializeToString</span><span class="p">(</span><span class="nx">vData</span><span class="p">)</span> <span class="o">:</span> <span class="nx">vData</span><span class="p">.</span><span class="nx">xml</span><span class="p">;</span></div><div class='line' id='LC267'>			<span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="k">this</span><span class="p">.</span><span class="nx">_headers</span><span class="p">[</span><span class="s2">&quot;Content-Type&quot;</span><span class="p">])</span> <span class="p">{</span></div><div class='line' id='LC268'>				<span class="k">this</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">setRequestHeader</span><span class="p">(</span><span class="s2">&quot;Content-Type&quot;</span><span class="p">,</span> <span class="s2">&quot;application/xml&quot;</span><span class="p">);</span></div><div class='line' id='LC269'>			<span class="p">}</span></div><div class='line' id='LC270'>		<span class="p">}</span></div><div class='line' id='LC271'><br/></div><div class='line' id='LC272'>		<span class="k">this</span><span class="p">.</span><span class="nx">_data</span> <span class="o">=</span> <span class="nx">vData</span><span class="p">;</span></div><div class='line' id='LC273'><br/></div><div class='line' id='LC274'>		<span class="cm">/**</span></div><div class='line' id='LC275'><span class="cm">		 * // Add to queue</span></div><div class='line' id='LC276'><span class="cm">		 * if (this._async) {</span></div><div class='line' id='LC277'><span class="cm">		 * 	fQueue_add(this);</span></div><div class='line' id='LC278'><span class="cm">		 * } else { */</span></div><div class='line' id='LC279'>		<span class="nx">fXMLHttpRequest_send</span><span class="p">(</span><span class="k">this</span><span class="p">);</span></div><div class='line' id='LC280'>		 <span class="cm">/**</span></div><div class='line' id='LC281'><span class="cm">		 * }</span></div><div class='line' id='LC282'><span class="cm">		 */</span></div><div class='line' id='LC283'>	<span class="p">};</span></div><div class='line' id='LC284'><br/></div><div class='line' id='LC285'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">abort</span> <span class="o">=</span> <span class="kd">function</span><span class="p">()</span> <span class="p">{</span></div><div class='line' id='LC286'>		<span class="c1">// Add method sniffer</span></div><div class='line' id='LC287'>		<span class="k">if</span> <span class="p">(</span><span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">onabort</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC288'>			<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">onabort</span><span class="p">.</span><span class="nx">apply</span><span class="p">(</span><span class="k">this</span><span class="p">,</span> <span class="nx">arguments</span><span class="p">);</span></div><div class='line' id='LC289'>		<span class="p">}</span></div><div class='line' id='LC290'><br/></div><div class='line' id='LC291'>		<span class="c1">// BUGFIX: Gecko - unnecessary DONE when aborting</span></div><div class='line' id='LC292'>		<span class="k">if</span> <span class="p">(</span><span class="k">this</span><span class="p">.</span><span class="nx">readyState</span> <span class="o">&gt;</span> <span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">UNSENT</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC293'>			<span class="k">this</span><span class="p">.</span><span class="nx">_aborted</span> <span class="o">=</span> <span class="kc">true</span><span class="p">;</span></div><div class='line' id='LC294'>		<span class="p">}</span></div><div class='line' id='LC295'><br/></div><div class='line' id='LC296'>		<span class="k">this</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">abort</span><span class="p">();</span></div><div class='line' id='LC297'><br/></div><div class='line' id='LC298'>		<span class="c1">// BUGFIX: IE - memory leak</span></div><div class='line' id='LC299'>		<span class="nx">fCleanTransport</span><span class="p">(</span><span class="k">this</span><span class="p">);</span></div><div class='line' id='LC300'><br/></div><div class='line' id='LC301'>		<span class="k">this</span><span class="p">.</span><span class="nx">readyState</span> <span class="o">=</span> <span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">UNSENT</span><span class="p">;</span></div><div class='line' id='LC302'><br/></div><div class='line' id='LC303'>		<span class="k">delete</span> <span class="k">this</span><span class="p">.</span><span class="nx">_data</span><span class="p">;</span></div><div class='line' id='LC304'><br/></div><div class='line' id='LC305'>		<span class="cm">/* if (this._async) {</span></div><div class='line' id='LC306'><span class="cm">	 	* 	fQueue_remove(this);</span></div><div class='line' id='LC307'><span class="cm">	 	* }</span></div><div class='line' id='LC308'><span class="cm">	 	*/</span></div><div class='line' id='LC309'>	<span class="p">};</span></div><div class='line' id='LC310'><br/></div><div class='line' id='LC311'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">getAllResponseHeaders</span> <span class="o">=</span> <span class="kd">function</span><span class="p">()</span> <span class="p">{</span></div><div class='line' id='LC312'>		<span class="k">return</span> <span class="k">this</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">getAllResponseHeaders</span><span class="p">();</span></div><div class='line' id='LC313'>	<span class="p">};</span></div><div class='line' id='LC314'><br/></div><div class='line' id='LC315'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">getResponseHeader</span> <span class="o">=</span> <span class="kd">function</span><span class="p">(</span><span class="nx">sName</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC316'>		<span class="k">return</span> <span class="k">this</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">getResponseHeader</span><span class="p">(</span><span class="nx">sName</span><span class="p">);</span></div><div class='line' id='LC317'>	<span class="p">};</span></div><div class='line' id='LC318'><br/></div><div class='line' id='LC319'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">setRequestHeader</span>  <span class="o">=</span> <span class="kd">function</span><span class="p">(</span><span class="nx">sName</span><span class="p">,</span> <span class="nx">sValue</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC320'>		<span class="c1">// BUGFIX: IE - cache issue</span></div><div class='line' id='LC321'>		<span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="k">this</span><span class="p">.</span><span class="nx">_headers</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC322'>			<span class="k">this</span><span class="p">.</span><span class="nx">_headers</span> <span class="o">=</span> <span class="p">{};</span></div><div class='line' id='LC323'>		<span class="p">}</span></div><div class='line' id='LC324'><br/></div><div class='line' id='LC325'>		<span class="k">this</span><span class="p">.</span><span class="nx">_headers</span><span class="p">[</span><span class="nx">sName</span><span class="p">]</span>  <span class="o">=</span> <span class="nx">sValue</span><span class="p">;</span></div><div class='line' id='LC326'><br/></div><div class='line' id='LC327'>		<span class="k">return</span> <span class="k">this</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">setRequestHeader</span><span class="p">(</span><span class="nx">sName</span><span class="p">,</span> <span class="nx">sValue</span><span class="p">);</span></div><div class='line' id='LC328'>	<span class="p">};</span></div><div class='line' id='LC329'><br/></div><div class='line' id='LC330'>	<span class="c1">// EventTarget interface implementation</span></div><div class='line' id='LC331'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">addEventListener</span>  <span class="o">=</span> <span class="kd">function</span><span class="p">(</span><span class="nx">sName</span><span class="p">,</span> <span class="nx">fHandler</span><span class="p">,</span> <span class="nx">bUseCapture</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC332'>		<span class="k">for</span> <span class="p">(</span><span class="kd">var</span> <span class="nx">nIndex</span> <span class="o">=</span> <span class="mi">0</span><span class="p">,</span> <span class="nx">oListener</span><span class="p">;</span> <span class="nx">oListener</span> <span class="o">=</span> <span class="k">this</span><span class="p">.</span><span class="nx">_listeners</span><span class="p">[</span><span class="nx">nIndex</span><span class="p">];</span> <span class="nx">nIndex</span><span class="o">++</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC333'>			<span class="k">if</span> <span class="p">(</span><span class="nx">oListener</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span> <span class="o">==</span> <span class="nx">sName</span> <span class="o">&amp;&amp;</span> <span class="nx">oListener</span><span class="p">[</span><span class="mi">1</span><span class="p">]</span> <span class="o">==</span> <span class="nx">fHandler</span> <span class="o">&amp;&amp;</span> <span class="nx">oListener</span><span class="p">[</span><span class="mi">2</span><span class="p">]</span> <span class="o">==</span> <span class="nx">bUseCapture</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC334'>				<span class="k">return</span><span class="p">;</span></div><div class='line' id='LC335'>			<span class="p">}</span></div><div class='line' id='LC336'>		<span class="p">}</span></div><div class='line' id='LC337'><br/></div><div class='line' id='LC338'>		<span class="c1">// Add listener</span></div><div class='line' id='LC339'>		<span class="k">this</span><span class="p">.</span><span class="nx">_listeners</span><span class="p">.</span><span class="nx">push</span><span class="p">([</span><span class="nx">sName</span><span class="p">,</span> <span class="nx">fHandler</span><span class="p">,</span> <span class="nx">bUseCapture</span><span class="p">]);</span></div><div class='line' id='LC340'>	<span class="p">};</span></div><div class='line' id='LC341'><br/></div><div class='line' id='LC342'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">removeEventListener</span> <span class="o">=</span> <span class="kd">function</span><span class="p">(</span><span class="nx">sName</span><span class="p">,</span> <span class="nx">fHandler</span><span class="p">,</span> <span class="nx">bUseCapture</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC343'>		<span class="k">for</span> <span class="p">(</span><span class="kd">var</span> <span class="nx">nIndex</span> <span class="o">=</span> <span class="mi">0</span><span class="p">,</span> <span class="nx">oListener</span><span class="p">;</span> <span class="nx">oListener</span> <span class="o">=</span> <span class="k">this</span><span class="p">.</span><span class="nx">_listeners</span><span class="p">[</span><span class="nx">nIndex</span><span class="p">];</span> <span class="nx">nIndex</span><span class="o">++</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC344'>			<span class="k">if</span> <span class="p">(</span><span class="nx">oListener</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span> <span class="o">==</span> <span class="nx">sName</span> <span class="o">&amp;&amp;</span> <span class="nx">oListener</span><span class="p">[</span><span class="mi">1</span><span class="p">]</span> <span class="o">==</span> <span class="nx">fHandler</span> <span class="o">&amp;&amp;</span> <span class="nx">oListener</span><span class="p">[</span><span class="mi">2</span><span class="p">]</span> <span class="o">==</span> <span class="nx">bUseCapture</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC345'>				<span class="k">break</span><span class="p">;</span></div><div class='line' id='LC346'>			<span class="p">}</span></div><div class='line' id='LC347'>		<span class="p">}</span></div><div class='line' id='LC348'><br/></div><div class='line' id='LC349'>		<span class="c1">// Remove listener</span></div><div class='line' id='LC350'>		<span class="k">if</span> <span class="p">(</span><span class="nx">oListener</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC351'>			<span class="k">this</span><span class="p">.</span><span class="nx">_listeners</span><span class="p">.</span><span class="nx">splice</span><span class="p">(</span><span class="nx">nIndex</span><span class="p">,</span> <span class="mi">1</span><span class="p">);</span></div><div class='line' id='LC352'>		<span class="p">}</span></div><div class='line' id='LC353'>	<span class="p">};</span></div><div class='line' id='LC354'><br/></div><div class='line' id='LC355'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">dispatchEvent</span> <span class="o">=</span> <span class="kd">function</span><span class="p">(</span><span class="nx">oEvent</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC356'>		<span class="kd">var</span> <span class="nx">oEventPseudo</span>  <span class="o">=</span> <span class="p">{</span></div><div class='line' id='LC357'>			<span class="s1">&#39;type&#39;</span><span class="o">:</span>             <span class="nx">oEvent</span><span class="p">.</span><span class="nx">type</span><span class="p">,</span></div><div class='line' id='LC358'>			<span class="s1">&#39;target&#39;</span><span class="o">:</span>           <span class="k">this</span><span class="p">,</span></div><div class='line' id='LC359'>			<span class="s1">&#39;currentTarget&#39;</span><span class="o">:</span>    <span class="k">this</span><span class="p">,</span></div><div class='line' id='LC360'>			<span class="s1">&#39;eventPhase&#39;</span><span class="o">:</span>       <span class="mi">2</span><span class="p">,</span></div><div class='line' id='LC361'>			<span class="s1">&#39;bubbles&#39;</span><span class="o">:</span>          <span class="nx">oEvent</span><span class="p">.</span><span class="nx">bubbles</span><span class="p">,</span></div><div class='line' id='LC362'>			<span class="s1">&#39;cancelable&#39;</span><span class="o">:</span>       <span class="nx">oEvent</span><span class="p">.</span><span class="nx">cancelable</span><span class="p">,</span></div><div class='line' id='LC363'>			<span class="s1">&#39;timeStamp&#39;</span><span class="o">:</span>        <span class="nx">oEvent</span><span class="p">.</span><span class="nx">timeStamp</span><span class="p">,</span></div><div class='line' id='LC364'>			<span class="s1">&#39;stopPropagation&#39;</span><span class="o">:</span>  <span class="kd">function</span><span class="p">()</span> <span class="p">{},</span>  <span class="c1">// There is no flow</span></div><div class='line' id='LC365'>			<span class="s1">&#39;preventDefault&#39;</span><span class="o">:</span>   <span class="kd">function</span><span class="p">()</span> <span class="p">{},</span>  <span class="c1">// There is no default action</span></div><div class='line' id='LC366'>			<span class="s1">&#39;initEvent&#39;</span><span class="o">:</span>        <span class="kd">function</span><span class="p">()</span> <span class="p">{}</span>   <span class="c1">// Original event object should be initialized</span></div><div class='line' id='LC367'>		<span class="p">};</span></div><div class='line' id='LC368'><br/></div><div class='line' id='LC369'>		<span class="c1">// Execute onreadystatechange</span></div><div class='line' id='LC370'>		<span class="k">if</span> <span class="p">(</span><span class="nx">oEventPseudo</span><span class="p">.</span><span class="nx">type</span> <span class="o">==</span> <span class="s2">&quot;readystatechange&quot;</span> <span class="o">&amp;&amp;</span> <span class="k">this</span><span class="p">.</span><span class="nx">onreadystatechange</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC371'>			<span class="p">(</span><span class="k">this</span><span class="p">.</span><span class="nx">onreadystatechange</span><span class="p">.</span><span class="nx">handleEvent</span> <span class="o">||</span> <span class="k">this</span><span class="p">.</span><span class="nx">onreadystatechange</span><span class="p">).</span><span class="nx">apply</span><span class="p">(</span><span class="k">this</span><span class="p">,</span> <span class="p">[</span><span class="nx">oEventPseudo</span><span class="p">]);</span></div><div class='line' id='LC372'>		<span class="p">}</span></div><div class='line' id='LC373'><br/></div><div class='line' id='LC374'><br/></div><div class='line' id='LC375'>		<span class="c1">// Execute listeners</span></div><div class='line' id='LC376'>		<span class="k">for</span> <span class="p">(</span><span class="kd">var</span> <span class="nx">nIndex</span> <span class="o">=</span> <span class="mi">0</span><span class="p">,</span> <span class="nx">oListener</span><span class="p">;</span> <span class="nx">oListener</span> <span class="o">=</span> <span class="k">this</span><span class="p">.</span><span class="nx">_listeners</span><span class="p">[</span><span class="nx">nIndex</span><span class="p">];</span> <span class="nx">nIndex</span><span class="o">++</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC377'>			<span class="k">if</span> <span class="p">(</span><span class="nx">oListener</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span> <span class="o">==</span> <span class="nx">oEventPseudo</span><span class="p">.</span><span class="nx">type</span> <span class="o">&amp;&amp;</span> <span class="o">!</span><span class="nx">oListener</span><span class="p">[</span><span class="mi">2</span><span class="p">])</span> <span class="p">{</span></div><div class='line' id='LC378'>				<span class="p">(</span><span class="nx">oListener</span><span class="p">[</span><span class="mi">1</span><span class="p">].</span><span class="nx">handleEvent</span> <span class="o">||</span> <span class="nx">oListener</span><span class="p">[</span><span class="mi">1</span><span class="p">]).</span><span class="nx">apply</span><span class="p">(</span><span class="k">this</span><span class="p">,</span> <span class="p">[</span><span class="nx">oEventPseudo</span><span class="p">]);</span></div><div class='line' id='LC379'>			<span class="p">}</span></div><div class='line' id='LC380'>		<span class="p">}</span></div><div class='line' id='LC381'><br/></div><div class='line' id='LC382'>	<span class="p">};</span></div><div class='line' id='LC383'><br/></div><div class='line' id='LC384'>	<span class="c1">//</span></div><div class='line' id='LC385'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">toString</span>  <span class="o">=</span> <span class="kd">function</span><span class="p">()</span> <span class="p">{</span></div><div class='line' id='LC386'>		<span class="k">return</span> <span class="s1">&#39;[&#39;</span> <span class="o">+</span> <span class="s2">&quot;object&quot;</span> <span class="o">+</span> <span class="s1">&#39; &#39;</span> <span class="o">+</span> <span class="s2">&quot;XMLHttpRequest&quot;</span> <span class="o">+</span> <span class="s1">&#39;]&#39;</span><span class="p">;</span></div><div class='line' id='LC387'>	<span class="p">};</span></div><div class='line' id='LC388'><br/></div><div class='line' id='LC389'>	<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">toString</span>  <span class="o">=</span> <span class="kd">function</span><span class="p">()</span> <span class="p">{</span></div><div class='line' id='LC390'>		<span class="k">return</span> <span class="s1">&#39;[&#39;</span> <span class="o">+</span> <span class="s2">&quot;XMLHttpRequest&quot;</span> <span class="o">+</span> <span class="s1">&#39;]&#39;</span><span class="p">;</span></div><div class='line' id='LC391'>	<span class="p">};</span></div><div class='line' id='LC392'><br/></div><div class='line' id='LC393'>	<span class="cm">/**</span></div><div class='line' id='LC394'><span class="cm">	 * // Queue manager</span></div><div class='line' id='LC395'><span class="cm">	 * var oQueuePending = {&quot;CRITICAL&quot;:[],&quot;HIGH&quot;:[],&quot;NORMAL&quot;:[],&quot;LOW&quot;:[],&quot;LOWEST&quot;:[]},</span></div><div class='line' id='LC396'><span class="cm">	 * aQueueRunning = [];</span></div><div class='line' id='LC397'><span class="cm">	 * function fQueue_add(oRequest) {</span></div><div class='line' id='LC398'><span class="cm">	 * 	oQueuePending[oRequest.priority in oQueuePending ? oRequest.priority : &quot;NORMAL&quot;].push(oRequest);</span></div><div class='line' id='LC399'><span class="cm">	 * 	//</span></div><div class='line' id='LC400'><span class="cm">	 * 	setTimeout(fQueue_process);</span></div><div class='line' id='LC401'><span class="cm">	 * };</span></div><div class='line' id='LC402'><span class="cm">	 *</span></div><div class='line' id='LC403'><span class="cm">	 * function fQueue_remove(oRequest) {</span></div><div class='line' id='LC404'><span class="cm">	 * 	for (var nIndex = 0, bFound = false; nIndex &lt; aQueueRunning.length; nIndex++)</span></div><div class='line' id='LC405'><span class="cm">	 * 	if (bFound) {</span></div><div class='line' id='LC406'><span class="cm">	 * 		aQueueRunning[nIndex - 1] = aQueueRunning[nIndex];</span></div><div class='line' id='LC407'><span class="cm">	 * 	} else {</span></div><div class='line' id='LC408'><span class="cm">	 * 		if (aQueueRunning[nIndex] == oRequest) {</span></div><div class='line' id='LC409'><span class="cm">	 * 			bFound  = true;</span></div><div class='line' id='LC410'><span class="cm">	 * 		}</span></div><div class='line' id='LC411'><span class="cm">	 * }</span></div><div class='line' id='LC412'><span class="cm">	 *</span></div><div class='line' id='LC413'><span class="cm">	 * 	if (bFound) {</span></div><div class='line' id='LC414'><span class="cm">	 * 		aQueueRunning.length--;</span></div><div class='line' id='LC415'><span class="cm">	 * 	}</span></div><div class='line' id='LC416'><span class="cm">	 *</span></div><div class='line' id='LC417'><span class="cm">	 *</span></div><div class='line' id='LC418'><span class="cm">	 * 	//</span></div><div class='line' id='LC419'><span class="cm">	 * 	setTimeout(fQueue_process);</span></div><div class='line' id='LC420'><span class="cm">	 * };</span></div><div class='line' id='LC421'><span class="cm">	 *</span></div><div class='line' id='LC422'><span class="cm">	 * function fQueue_process() {</span></div><div class='line' id='LC423'><span class="cm">	 * if (aQueueRunning.length &lt; 6) {</span></div><div class='line' id='LC424'><span class="cm">	 * for (var sPriority in oQueuePending) {</span></div><div class='line' id='LC425'><span class="cm">	 * if (oQueuePending[sPriority].length) {</span></div><div class='line' id='LC426'><span class="cm">	 * var oRequest  = oQueuePending[sPriority][0];</span></div><div class='line' id='LC427'><span class="cm">	 * oQueuePending[sPriority]  = oQueuePending[sPriority].slice(1);</span></div><div class='line' id='LC428'><span class="cm">	 * //</span></div><div class='line' id='LC429'><span class="cm">	 * aQueueRunning.push(oRequest);</span></div><div class='line' id='LC430'><span class="cm">	 * // Send request</span></div><div class='line' id='LC431'><span class="cm">	 * fXMLHttpRequest_send(oRequest);</span></div><div class='line' id='LC432'><span class="cm">	 * break;</span></div><div class='line' id='LC433'><span class="cm">	 * }</span></div><div class='line' id='LC434'><span class="cm">	 * }</span></div><div class='line' id='LC435'><span class="cm">	 * }</span></div><div class='line' id='LC436'><span class="cm">	 * };</span></div><div class='line' id='LC437'><span class="cm">	 */</span></div><div class='line' id='LC438'><br/></div><div class='line' id='LC439'>	<span class="c1">// Helper function</span></div><div class='line' id='LC440'>	<span class="kd">function</span> <span class="nx">fXMLHttpRequest_send</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC441'>		<span class="nx">oRequest</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">send</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">.</span><span class="nx">_data</span><span class="p">);</span></div><div class='line' id='LC442'><br/></div><div class='line' id='LC443'>		<span class="c1">// BUGFIX: Gecko - missing readystatechange calls in synchronous requests</span></div><div class='line' id='LC444'>		<span class="k">if</span> <span class="p">(</span><span class="nx">bGecko</span> <span class="o">&amp;&amp;</span> <span class="o">!</span><span class="nx">oRequest</span><span class="p">.</span><span class="nx">_async</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC445'>			<span class="nx">oRequest</span><span class="p">.</span><span class="nx">readyState</span> <span class="o">=</span> <span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">OPENED</span><span class="p">;</span></div><div class='line' id='LC446'><br/></div><div class='line' id='LC447'>			<span class="c1">// Synchronize state</span></div><div class='line' id='LC448'>			<span class="nx">fSynchronizeValues</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">);</span></div><div class='line' id='LC449'><br/></div><div class='line' id='LC450'>			<span class="c1">// Simulate missing states</span></div><div class='line' id='LC451'>			<span class="k">while</span> <span class="p">(</span><span class="nx">oRequest</span><span class="p">.</span><span class="nx">readyState</span> <span class="o">&lt;</span> <span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">DONE</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC452'>				<span class="nx">oRequest</span><span class="p">.</span><span class="nx">readyState</span><span class="o">++</span><span class="p">;</span></div><div class='line' id='LC453'>				<span class="nx">fReadyStateChange</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">);</span></div><div class='line' id='LC454'>				<span class="c1">// Check if we are aborted</span></div><div class='line' id='LC455'>				<span class="k">if</span> <span class="p">(</span><span class="nx">oRequest</span><span class="p">.</span><span class="nx">_aborted</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC456'>					<span class="k">return</span><span class="p">;</span></div><div class='line' id='LC457'>				<span class="p">}</span></div><div class='line' id='LC458'>			<span class="p">}</span></div><div class='line' id='LC459'>		<span class="p">}</span></div><div class='line' id='LC460'>	<span class="p">}</span></div><div class='line' id='LC461'><br/></div><div class='line' id='LC462'>	<span class="kd">function</span> <span class="nx">fReadyStateChange</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC463'>		<span class="c1">// Sniffing code</span></div><div class='line' id='LC464'>		<span class="k">if</span> <span class="p">(</span><span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">onreadystatechange</span><span class="p">){</span></div><div class='line' id='LC465'>			<span class="nx">cXMLHttpRequest</span><span class="p">.</span><span class="nx">onreadystatechange</span><span class="p">.</span><span class="nx">apply</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">);</span></div><div class='line' id='LC466'>		<span class="p">}</span></div><div class='line' id='LC467'><br/></div><div class='line' id='LC468'><br/></div><div class='line' id='LC469'>		<span class="c1">// Fake event</span></div><div class='line' id='LC470'>		<span class="nx">oRequest</span><span class="p">.</span><span class="nx">dispatchEvent</span><span class="p">({</span></div><div class='line' id='LC471'>			<span class="s1">&#39;type&#39;</span><span class="o">:</span>       <span class="s2">&quot;readystatechange&quot;</span><span class="p">,</span></div><div class='line' id='LC472'>			<span class="s1">&#39;bubbles&#39;</span><span class="o">:</span>    <span class="kc">false</span><span class="p">,</span></div><div class='line' id='LC473'>			<span class="s1">&#39;cancelable&#39;</span><span class="o">:</span> <span class="kc">false</span><span class="p">,</span></div><div class='line' id='LC474'>			<span class="s1">&#39;timeStamp&#39;</span><span class="o">:</span>  <span class="k">new</span> <span class="nb">Date</span> <span class="o">+</span> <span class="mi">0</span></div><div class='line' id='LC475'>		<span class="p">});</span></div><div class='line' id='LC476'>	<span class="p">}</span></div><div class='line' id='LC477'><br/></div><div class='line' id='LC478'>	<span class="kd">function</span> <span class="nx">fGetDocument</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC479'>		<span class="kd">var</span> <span class="nx">oDocument</span> <span class="o">=</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">responseXML</span><span class="p">;</span></div><div class='line' id='LC480'>		<span class="kd">var</span> <span class="nx">sResponse</span> <span class="o">=</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">responseText</span><span class="p">;</span></div><div class='line' id='LC481'>		<span class="c1">// Try parsing responseText</span></div><div class='line' id='LC482'>		<span class="k">if</span> <span class="p">(</span><span class="nx">bIE</span> <span class="o">&amp;&amp;</span> <span class="nx">sResponse</span> <span class="o">&amp;&amp;</span> <span class="nx">oDocument</span> <span class="o">&amp;&amp;</span> <span class="o">!</span><span class="nx">oDocument</span><span class="p">.</span><span class="nx">documentElement</span> <span class="o">&amp;&amp;</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">getResponseHeader</span><span class="p">(</span><span class="s2">&quot;Content-Type&quot;</span><span class="p">).</span><span class="nx">match</span><span class="p">(</span><span class="sr">/[^\/]+\/[^\+]+\+xml/</span><span class="p">))</span> <span class="p">{</span></div><div class='line' id='LC483'>			<span class="nx">oDocument</span> <span class="o">=</span> <span class="k">new</span> <span class="nb">window</span><span class="p">.</span><span class="nx">ActiveXObject</span><span class="p">(</span><span class="s2">&quot;Microsoft.XMLDOM&quot;</span><span class="p">);</span></div><div class='line' id='LC484'>			<span class="nx">oDocument</span><span class="p">.</span><span class="nx">async</span>       <span class="o">=</span> <span class="kc">false</span><span class="p">;</span></div><div class='line' id='LC485'>			<span class="nx">oDocument</span><span class="p">.</span><span class="nx">validateOnParse</span> <span class="o">=</span> <span class="kc">false</span><span class="p">;</span></div><div class='line' id='LC486'>			<span class="nx">oDocument</span><span class="p">.</span><span class="nx">loadXML</span><span class="p">(</span><span class="nx">sResponse</span><span class="p">);</span></div><div class='line' id='LC487'>		<span class="p">}</span></div><div class='line' id='LC488'><br/></div><div class='line' id='LC489'>		<span class="c1">// Check if there is no error in document</span></div><div class='line' id='LC490'>		<span class="k">if</span> <span class="p">(</span><span class="nx">oDocument</span><span class="p">){</span></div><div class='line' id='LC491'>			<span class="k">if</span> <span class="p">((</span><span class="nx">bIE</span> <span class="o">&amp;&amp;</span> <span class="nx">oDocument</span><span class="p">.</span><span class="nx">parseError</span> <span class="o">!==</span> <span class="mi">0</span><span class="p">)</span> <span class="o">||</span> <span class="o">!</span><span class="nx">oDocument</span><span class="p">.</span><span class="nx">documentElement</span> <span class="o">||</span> <span class="p">(</span><span class="nx">oDocument</span><span class="p">.</span><span class="nx">documentElement</span> <span class="o">&amp;&amp;</span> <span class="nx">oDocument</span><span class="p">.</span><span class="nx">documentElement</span><span class="p">.</span><span class="nx">tagName</span> <span class="o">==</span> <span class="s2">&quot;parsererror&quot;</span><span class="p">))</span> <span class="p">{</span></div><div class='line' id='LC492'>				<span class="k">return</span> <span class="kc">null</span><span class="p">;</span></div><div class='line' id='LC493'>			<span class="p">}</span></div><div class='line' id='LC494'>		<span class="p">}</span></div><div class='line' id='LC495'>		<span class="k">return</span> <span class="nx">oDocument</span><span class="p">;</span></div><div class='line' id='LC496'>	<span class="p">}</span></div><div class='line' id='LC497'><br/></div><div class='line' id='LC498'>	<span class="kd">function</span> <span class="nx">fSynchronizeValues</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC499'>		<span class="k">try</span> <span class="p">{</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">responseText</span> <span class="o">=</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">responseText</span><span class="p">;</span>  <span class="p">}</span> <span class="k">catch</span> <span class="p">(</span><span class="nx">e</span><span class="p">)</span> <span class="p">{}</span></div><div class='line' id='LC500'>		<span class="k">try</span> <span class="p">{</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">responseXML</span>  <span class="o">=</span> <span class="nx">fGetDocument</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">.</span><span class="nx">_object</span><span class="p">);</span> <span class="p">}</span> <span class="k">catch</span> <span class="p">(</span><span class="nx">e</span><span class="p">)</span> <span class="p">{}</span></div><div class='line' id='LC501'>		<span class="k">try</span> <span class="p">{</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">status</span>       <span class="o">=</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">status</span><span class="p">;</span>        <span class="p">}</span> <span class="k">catch</span> <span class="p">(</span><span class="nx">e</span><span class="p">)</span> <span class="p">{}</span></div><div class='line' id='LC502'>		<span class="k">try</span> <span class="p">{</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">statusText</span>   <span class="o">=</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">statusText</span><span class="p">;</span>    <span class="p">}</span> <span class="k">catch</span> <span class="p">(</span><span class="nx">e</span><span class="p">)</span> <span class="p">{}</span></div><div class='line' id='LC503'>	<span class="p">}</span></div><div class='line' id='LC504'><br/></div><div class='line' id='LC505'>	<span class="kd">function</span> <span class="nx">fCleanTransport</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC506'>		<span class="c1">// BUGFIX: IE - memory leak (on-page leak)</span></div><div class='line' id='LC507'>		<span class="nx">oRequest</span><span class="p">.</span><span class="nx">_object</span><span class="p">.</span><span class="nx">onreadystatechange</span> <span class="o">=</span> <span class="k">new</span> <span class="nb">window</span><span class="p">.</span><span class="nb">Function</span><span class="p">;</span></div><div class='line' id='LC508'>	<span class="p">}</span></div><div class='line' id='LC509'><br/></div><div class='line' id='LC510'>	<span class="c1">// Internet Explorer 5.0 (missing apply)</span></div><div class='line' id='LC511'>	<span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="nb">window</span><span class="p">.</span><span class="nb">Function</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">apply</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC512'>		<span class="nb">window</span><span class="p">.</span><span class="nb">Function</span><span class="p">.</span><span class="nx">prototype</span><span class="p">.</span><span class="nx">apply</span> <span class="o">=</span> <span class="kd">function</span><span class="p">(</span><span class="nx">oRequest</span><span class="p">,</span> <span class="nx">oArguments</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC513'>			<span class="k">if</span> <span class="p">(</span><span class="o">!</span><span class="nx">oArguments</span><span class="p">)</span> <span class="p">{</span></div><div class='line' id='LC514'>				<span class="nx">oArguments</span>  <span class="o">=</span> <span class="p">[];</span></div><div class='line' id='LC515'>			<span class="p">}</span></div><div class='line' id='LC516'>			<span class="nx">oRequest</span><span class="p">.</span><span class="nx">__func</span> <span class="o">=</span> <span class="k">this</span><span class="p">;</span></div><div class='line' id='LC517'>			<span class="nx">oRequest</span><span class="p">.</span><span class="nx">__func</span><span class="p">(</span><span class="nx">oArguments</span><span class="p">[</span><span class="mi">0</span><span class="p">],</span> <span class="nx">oArguments</span><span class="p">[</span><span class="mi">1</span><span class="p">],</span> <span class="nx">oArguments</span><span class="p">[</span><span class="mi">2</span><span class="p">],</span> <span class="nx">oArguments</span><span class="p">[</span><span class="mi">3</span><span class="p">],</span> <span class="nx">oArguments</span><span class="p">[</span><span class="mi">4</span><span class="p">]);</span></div><div class='line' id='LC518'>			<span class="k">delete</span> <span class="nx">oRequest</span><span class="p">.</span><span class="nx">__func</span><span class="p">;</span></div><div class='line' id='LC519'>		<span class="p">};</span></div><div class='line' id='LC520'>	<span class="p">}</span></div><div class='line' id='LC521'><br/></div><div class='line' id='LC522'>	<span class="c1">// Register new object with window</span></div><div class='line' id='LC523'>	<span class="nb">window</span><span class="p">.</span><span class="nx">XMLHttpRequest</span> <span class="o">=</span> <span class="nx">cXMLHttpRequest</span><span class="p">;</span></div><div class='line' id='LC524'><br/></div><div class='line' id='LC525'><span class="p">})();</span></div></pre></div>
          </td>
        </tr>
      </table>
  </div>

          </div>
        </div>
      </div>
    </div>
</div>

<div class="frame frame-loading large-loading-area" style="display:none;" data-tree-list-url="/ilinsky/xmlhttprequest/tree-list/b5728e32124b44981a19fefb78d6a2a1c3033413">
  <img src="https://a248.e.akamai.net/assets.github.com/images/spinners/octocat-spinner-128.gif?1347543527" height="64" width="64">
</div>

        </div>
      </div>
      <div class="context-overlay"></div>
    </div>

      <div id="footer-push"></div><!-- hack for sticky footer -->
    </div><!-- end of wrapper - hack for sticky footer -->

      <!-- footer -->
      <div id="footer" >
        
  <div class="upper_footer">
     <div class="container clearfix">

       <h4 id="blacktocat">GitHub Links</h4>

       <ul class="footer_nav">
         <h4>GitHub</h4>
         <li><a href="https://github.com/about">About</a></li>
         <li><a href="https://github.com/blog">Blog</a></li>
         <li><a href="https://github.com/features">Features</a></li>
         <li><a href="https://github.com/contact">Contact &amp; Support</a></li>
         <li><a href="http://training.github.com/">Training</a></li>
         <li><a href="http://enterprise.github.com/">GitHub Enterprise</a></li>
         <li><a href="http://status.github.com/">Site Status</a></li>
       </ul>

       <ul class="footer_nav">
         <h4>Clients</h4>
         <li><a href="http://mac.github.com/">GitHub for Mac</a></li>
         <li><a href="http://windows.github.com/">GitHub for Windows</a></li>
         <li><a href="http://eclipse.github.com/">GitHub for Eclipse</a></li>
         <li><a href="http://mobile.github.com/">GitHub Mobile Apps</a></li>
       </ul>

       <ul class="footer_nav">
         <h4>Tools</h4>
         <li><a href="http://get.gaug.es/">Gauges: Web analytics</a></li>
         <li><a href="http://speakerdeck.com">Speaker Deck: Presentations</a></li>
         <li><a href="https://gist.github.com">Gist: Code snippets</a></li>

         <h4 class="second">Extras</h4>
         <li><a href="http://jobs.github.com/">Job Board</a></li>
         <li><a href="http://shop.github.com/">GitHub Shop</a></li>
         <li><a href="http://octodex.github.com/">The Octodex</a></li>
       </ul>

       <ul class="footer_nav">
         <h4>Documentation</h4>
         <li><a href="http://help.github.com/">GitHub Help</a></li>
         <li><a href="http://developer.github.com/">Developer API</a></li>
         <li><a href="http://github.github.com/github-flavored-markdown/">GitHub Flavored Markdown</a></li>
         <li><a href="http://pages.github.com/">GitHub Pages</a></li>
       </ul>

     </div><!-- /.site -->
  </div><!-- /.upper_footer -->

<div class="lower_footer">
  <div class="container clearfix">
    <div id="legal">
      <ul>
          <li><a href="https://github.com/site/terms">Terms of Service</a></li>
          <li><a href="https://github.com/site/privacy">Privacy</a></li>
          <li><a href="https://github.com/security">Security</a></li>
      </ul>

      <p>&copy; 2012 <span title="0.07721s from fe16.rs.github.com">GitHub</span> Inc. All rights reserved.</p>
    </div><!-- /#legal or /#legal_ie-->

  </div><!-- /.site -->
</div><!-- /.lower_footer -->


      </div><!-- /#footer -->

    

<div id="keyboard_shortcuts_pane" class="instapaper_ignore readability-extra" style="display:none">
  <h2>Keyboard Shortcuts <small><a href="#" class="js-see-all-keyboard-shortcuts">(see all)</a></small></h2>

  <div class="columns threecols">
    <div class="column first">
      <h3>Site wide shortcuts</h3>
      <dl class="keyboard-mappings">
        <dt>s</dt>
        <dd>Focus command bar</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>?</dt>
        <dd>Bring up this help dialog</dd>
      </dl>
    </div><!-- /.column.first -->

    <div class="column middle" style='display:none'>
      <h3>Commit list</h3>
      <dl class="keyboard-mappings">
        <dt>j</dt>
        <dd>Move selection down</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>k</dt>
        <dd>Move selection up</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>c <em>or</em> o <em>or</em> enter</dt>
        <dd>Open commit</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>y</dt>
        <dd>Expand URL to its canonical form</dd>
      </dl>
    </div><!-- /.column.first -->

    <div class="column last js-hidden-pane" style='display:none'>
      <h3>Pull request list</h3>
      <dl class="keyboard-mappings">
        <dt>j</dt>
        <dd>Move selection down</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>k</dt>
        <dd>Move selection up</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt>o <em>or</em> enter</dt>
        <dd>Open issue</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt><span class="platform-mac">⌘</span><span class="platform-other">ctrl</span> <em>+</em> enter</dt>
        <dd>Submit comment</dd>
      </dl>
      <dl class="keyboard-mappings">
        <dt><span class="platform-mac">⌘</span><span class="platform-other">ctrl</span> <em>+</em> shift p</dt>
        <dd>Preview comment</dd>
      </dl>
    </div><!-- /.columns.last -->

  </div><!-- /.columns.equacols -->

  <div class="js-hidden-pane" style='display:none'>
    <div class="rule"></div>

    <h3>Issues</h3>

    <div class="columns threecols">
      <div class="column first">
        <dl class="keyboard-mappings">
          <dt>j</dt>
          <dd>Move selection down</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>k</dt>
          <dd>Move selection up</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>x</dt>
          <dd>Toggle selection</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>o <em>or</em> enter</dt>
          <dd>Open issue</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt><span class="platform-mac">⌘</span><span class="platform-other">ctrl</span> <em>+</em> enter</dt>
          <dd>Submit comment</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt><span class="platform-mac">⌘</span><span class="platform-other">ctrl</span> <em>+</em> shift p</dt>
          <dd>Preview comment</dd>
        </dl>
      </div><!-- /.column.first -->
      <div class="column last">
        <dl class="keyboard-mappings">
          <dt>c</dt>
          <dd>Create issue</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>l</dt>
          <dd>Create label</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>i</dt>
          <dd>Back to inbox</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>u</dt>
          <dd>Back to issues</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>/</dt>
          <dd>Focus issues search</dd>
        </dl>
      </div>
    </div>
  </div>

  <div class="js-hidden-pane" style='display:none'>
    <div class="rule"></div>

    <h3>Issues Dashboard</h3>

    <div class="columns threecols">
      <div class="column first">
        <dl class="keyboard-mappings">
          <dt>j</dt>
          <dd>Move selection down</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>k</dt>
          <dd>Move selection up</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>o <em>or</em> enter</dt>
          <dd>Open issue</dd>
        </dl>
      </div><!-- /.column.first -->
    </div>
  </div>

  <div class="js-hidden-pane" style='display:none'>
    <div class="rule"></div>

    <h3>Network Graph</h3>
    <div class="columns equacols">
      <div class="column first">
        <dl class="keyboard-mappings">
          <dt><span class="badmono">←</span> <em>or</em> h</dt>
          <dd>Scroll left</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt><span class="badmono">→</span> <em>or</em> l</dt>
          <dd>Scroll right</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt><span class="badmono">↑</span> <em>or</em> k</dt>
          <dd>Scroll up</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt><span class="badmono">↓</span> <em>or</em> j</dt>
          <dd>Scroll down</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>t</dt>
          <dd>Toggle visibility of head labels</dd>
        </dl>
      </div><!-- /.column.first -->
      <div class="column last">
        <dl class="keyboard-mappings">
          <dt>shift <span class="badmono">←</span> <em>or</em> shift h</dt>
          <dd>Scroll all the way left</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>shift <span class="badmono">→</span> <em>or</em> shift l</dt>
          <dd>Scroll all the way right</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>shift <span class="badmono">↑</span> <em>or</em> shift k</dt>
          <dd>Scroll all the way up</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>shift <span class="badmono">↓</span> <em>or</em> shift j</dt>
          <dd>Scroll all the way down</dd>
        </dl>
      </div><!-- /.column.last -->
    </div>
  </div>

  <div class="js-hidden-pane" >
    <div class="rule"></div>
    <div class="columns threecols">
      <div class="column first js-hidden-pane" >
        <h3>Source Code Browsing</h3>
        <dl class="keyboard-mappings">
          <dt>t</dt>
          <dd>Activates the file finder</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>l</dt>
          <dd>Jump to line</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>w</dt>
          <dd>Switch branch/tag</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>y</dt>
          <dd>Expand URL to its canonical form</dd>
        </dl>
      </div>
    </div>
  </div>

  <div class="js-hidden-pane" style='display:none'>
    <div class="rule"></div>
    <div class="columns threecols">
      <div class="column first">
        <h3>Browsing Commits</h3>
        <dl class="keyboard-mappings">
          <dt><span class="platform-mac">⌘</span><span class="platform-other">ctrl</span> <em>+</em> enter</dt>
          <dd>Submit comment</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>escape</dt>
          <dd>Close form</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>p</dt>
          <dd>Parent commit</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>o</dt>
          <dd>Other parent commit</dd>
        </dl>
      </div>
    </div>
  </div>

  <div class="js-hidden-pane" style='display:none'>
    <div class="rule"></div>
    <h3>Notifications</h3>

    <div class="columns threecols">
      <div class="column first">
        <dl class="keyboard-mappings">
          <dt>j</dt>
          <dd>Move selection down</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>k</dt>
          <dd>Move selection up</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>o <em>or</em> enter</dt>
          <dd>Open notification</dd>
        </dl>
      </div><!-- /.column.first -->

      <div class="column second">
        <dl class="keyboard-mappings">
          <dt>e <em>or</em> shift i <em>or</em> y</dt>
          <dd>Mark as read</dd>
        </dl>
        <dl class="keyboard-mappings">
          <dt>shift m</dt>
          <dd>Mute thread</dd>
        </dl>
      </div><!-- /.column.first -->
    </div>
  </div>

</div>

    <div id="markdown-help" class="instapaper_ignore readability-extra">
  <h2>Markdown Cheat Sheet</h2>

  <div class="cheatsheet-content">

  <div class="mod">
    <div class="col">
      <h3>Format Text</h3>
      <p>Headers</p>
      <pre>
# This is an &lt;h1&gt; tag
## This is an &lt;h2&gt; tag
###### This is an &lt;h6&gt; tag</pre>
     <p>Text styles</p>
     <pre>
*This text will be italic*
_This will also be italic_
**This text will be bold**
__This will also be bold__

*You **can** combine them*
</pre>
    </div>
    <div class="col">
      <h3>Lists</h3>
      <p>Unordered</p>
      <pre>
* Item 1
* Item 2
  * Item 2a
  * Item 2b</pre>
     <p>Ordered</p>
     <pre>
1. Item 1
2. Item 2
3. Item 3
   * Item 3a
   * Item 3b</pre>
    </div>
    <div class="col">
      <h3>Miscellaneous</h3>
      <p>Images</p>
      <pre>
![GitHub Logo](/images/logo.png)
Format: ![Alt Text](url)
</pre>
     <p>Links</p>
     <pre>
http://github.com - automatic!
[GitHub](http://github.com)</pre>
<p>Blockquotes</p>
     <pre>
As Kanye West said:

> We're living the future so
> the present is our past.
</pre>
    </div>
  </div>
  <div class="rule"></div>

  <h3>Code Examples in Markdown</h3>
  <div class="col">
      <p>Syntax highlighting with <a href="http://github.github.com/github-flavored-markdown/" title="GitHub Flavored Markdown" target="_blank">GFM</a></p>
      <pre>
```javascript
function fancyAlert(arg) {
  if(arg) {
    $.facebox({div:'#foo'})
  }
}
```</pre>
    </div>
    <div class="col">
      <p>Or, indent your code 4 spaces</p>
      <pre>
Here is a Python code example
without syntax highlighting:

    def foo:
      if not bar:
        return true</pre>
    </div>
    <div class="col">
      <p>Inline code for comments</p>
      <pre>
I think you should use an
`&lt;addr&gt;` element here instead.</pre>
    </div>
  </div>

  </div>
</div>


    <div id="ajax-error-message" class="flash flash-error">
      <span class="mini-icon mini-icon-exclamation"></span>
      Something went wrong with that request. Please try again.
      <a href="#" class="mini-icon mini-icon-remove-close ajax-error-dismiss"></a>
    </div>

    <div id="logo-popup">
      <h2>Looking for the GitHub logo?</h2>
      <ul>
        <li>
          <h4>GitHub Logo</h4>
          <a href="http://github-media-downloads.s3.amazonaws.com/GitHub_Logos.zip"><img alt="Github_logo" src="https://a248.e.akamai.net/assets.github.com/images/modules/about_page/github_logo.png?1340659511" /></a>
          <a href="http://github-media-downloads.s3.amazonaws.com/GitHub_Logos.zip" class="minibutton download">Download</a>
        </li>
        <li>
          <h4>The Octocat</h4>
          <a href="http://github-media-downloads.s3.amazonaws.com/Octocats.zip"><img alt="Octocat" src="https://a248.e.akamai.net/assets.github.com/images/modules/about_page/octocat.png?1340659511" /></a>
          <a href="http://github-media-downloads.s3.amazonaws.com/Octocats.zip" class="minibutton download">Download</a>
        </li>
      </ul>
    </div>

    
    
    <span id='server_response_time' data-time='0.07896' data-host='fe16'></span>
    
  </body>
</html>

