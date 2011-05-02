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
                div({'class': 'voting'})
            );
        });
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
        var voteDiv = this.element.getElement('.voting');
        var upVote = this.renderTemplate('TMIVoteForm', {
            tweetId: this.tweetId,
            voteValue: 1
        });
        upVote.addEvent('submit', this.submitVote);

        var downVote = this.renderTemplate('TMIVoteForm', {
            tweetId: this.tweetId,
            voteValue: -1
        });
        downVote.addEvent('submit', this.submitVote);
        voteDiv.adopt(upVote, downVote);
    },

    submitVote: function(e) {
        e.preventDefault();
        this.send();
    },

    toElement: function() {
        return this.element;
    },

    fadeIn: function() {
        this.element.set('opacity', 0);
        new Fx.Tween(this.element, {
            duration: 400,
            property: 'opacity'
        }).start(0, 1);
    }
      
});

var oversharers = {
    twitterLink: function(username) {
        return "http://twitter.com/" + username;
    },
    createTweets: function(data) {
        var tweets = data['tweets'];
        var tweetViews = tweets.map(function(tweetData) {
            return new TMITweetView(tweetData);
        });
        var tweetContainer = $('tweets');
        Array.each(tweetViews, function(tweetView, index) {
            var showTweet = function() {
                tweetView.fadeIn();
                $(tweetView).inject(tweetContainer);
            };
            showTweet.delay(index * 100);
        });
    }
}

window.addEvent('domready', function() {
    new Request.JSON({
        url: '../tweets/',
        method: 'get',
        onSuccess: oversharers.createTweets
    }).send();
});
