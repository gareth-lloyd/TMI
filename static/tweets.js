var TMITweetView = new Class({
    Implements: Mooml.Templates,
    initialize: function(data) {
        Object.append(this, data);
        this.registerTemplate('TMITweetView', function(data) {
            div({'class': 'tweet'},
                div({'class': 'tweet-image'},
                    img({src: data.imageUrl})
                ),
                div({'class': 'twitter-username'},
                    a({href: oversharers.twitterLink(data.twitterUsername)},
                    data.twitterUsername)
                ),
                div({'class': 'tweet-text'},
                    '"' + data.text + '"'
                ),
                div({'class': 'votes'}, data.upVotes),
                div({'class': 'voting'}),
                div({'class': 'errors'})
            );
        });
    },
    toElement: function() {
        return this.element;
    }
});
var TMICandidateTweet = new Class({
    Extends: TMITweetView,
    initialize: function(data) {
        this.parent(data);
        this.registerTemplate('TMIVoteForm', function(voteData) {
            form({method: 'post', action: '../tweets/' + voteData.tweetId + '/vote/'},
                input({'class': 'vote-value',
                    name: 'vote',
                    type: 'hidden',
                    value: '' + voteData.voteValue}),
                input({'class': 'vote-button value' + voteData.voteValue,
                    type: 'submit',
                    value: '' + voteData.voteValue})
            );
        });
        this.element = this.renderTemplate('TMITweetView', this);
        this.setUpVoting();
    },

    setUpVoting: function() {
        this.voteDiv = this.element.getElement('.voting');
        this.upVote = this.renderTemplate('TMIVoteForm', {
            tweetId: this.tweetId,
            voteValue: 1
        });
        this.downVote = this.renderTemplate('TMIVoteForm', {
            tweetId: this.tweetId,
            voteValue: -1
        });

        var submitVote = function(e) {
            e.preventDefault();
            this.send();
        }

        this.upVote.addEvent('submit', submitVote);
        this.upVote.set('send', {
            onSuccess: this.haveUpVoted.bind(this),
            onFailure: this.voteFailed.bind(this)
        });

        this.downVote.addEvent('submit', submitVote);
        this.downVote.set('send', {
            onSuccess: this.haveDownVoted.bind(this),
            onFailure: this.voteFailed.bind(this)
        });

        if (oversharers.userVotes[this.tweetId]) {
            this.haveUpVoted();
        } else {
            this.haveDownVoted();
        }
    },

    haveUpVoted: function(response) {
        this.updateVotes(response);
        this.voteDiv.getChildren().each(function(el) {el.dispose()});
        this.voteDiv.grab(this.downVote);
        // clear any previous errors:
        this.element.getElement('.errors').set('text', '');
        // TODO show vote effect
    },
    updateVotes: function(response) {
        if (response == undefined)
            return;
        var voteVal = JSON.parse(response)['acceptedVote'];
        this.upVotes += voteVal;
        this.element.getElement('.votes').set('text', this.upVotes);
    },
    haveDownVoted: function(response) {
        this.updateVotes(response);
        this.voteDiv.getChildren().each(function(el) {el.dispose()});
        this.voteDiv.grab(this.upVote);
        this.element.getElement('.errors').set('text', '');
        // TODO show vote effect
    },
    voteFailed: function(response) {
        var error = JSON.parse(response.responseText);
        this.element.getElement('.errors').set('text', error['error']);
    },
    fadeIn: function() {
        this.element.set('opacity', 0);
        new Fx.Tween(this.element, {
            duration: 400,
            property: 'opacity'
        }).start(0, 1);
    }
});

var TMIWinnerView = new Class({
    Extends: TMITweetView,
    initialize: function(data) {
        this.parent(data);
        Object.append(this, data);
        this.element = this.renderTemplate('TMITweetView', this);
    },
});

var oversharers = {
    userVotes: {},

    twitterLink: function(username) {
        return "http://twitter.com/" + username;
    },
    createTweets: function(data) {
        oversharers.setUpUserVotes();

        var tweets = data['tweets'];
        var tweetViews = tweets.map(function(tweetData) {
            return new TMICandidateTweet(tweetData);
        });
        var tweetContainer = $('tweets');
        Array.each(tweetViews, function(tweetView, index) {
            var showTweet = function() {
                tweetView.fadeIn();
                $(tweetView).inject(tweetContainer);
            };
            showTweet.delay(index * 100);
        });
    },
    createWinner: function(data) {
        var winnerContainer = $('winner');
        var winner = new TMIWinnerView(data.winner);
        winner.toElement().inject(winnerContainer);
    },
    setUpUserVotes: function() {
        var cookieVal = Cookie.read('displayvotes')
        if (cookieVal) {
            ids = cookieVal.split('|');
            Array.each(ids, function(id){
                oversharers.userVotes[id] = true;
            });
        }
    }
}

window.addEvent('domready', function() {
    new Request.JSON({
        url: '../tweets/',
        method: 'get',
        onSuccess: oversharers.createTweets
    }).send();
    new Request.JSON({
        url: '../tweets/winner/',
        method: 'get',
        onSuccess: oversharers.createWinner
    }).send();
});
