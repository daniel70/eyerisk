Vue.component('app-view', {
    template: '<div id="my-view">This is a very important secret...</div>'
})

var app = new Vue({
    el: '#app',
    data: {
        message: 'Hello Vue!',
        people: [
            {
                name: 'Daniel',
                age: 47,
            },
            {
                name: 'Pim',
                age: 48,
            },
            {
                name: 'Sofie',
                age: 14,
            }
        ]
    }
})


var obj = {
    el: '#example',
    data: {
        message: 'Hello',
        firstName: "Daniel",
        lastName: "van der Meulen"
    },
    props: ['labelText'], // props are passed from parent to child
    computed: { // these methods are cached based on their dependencies
        reversedMessage: function () {
            return this.message.split('').reverse().join('')
        },
        fullName: {
            get: function () { // normally functions are get only
                return this.firstName + ' ' + this.lastName
            },
            set: function (newValue) { // a function can have a setter method
                var names = newValue.split(' ')
                this.firstName = names[0]
                this.lastName = names[names.length - 1]
            }
        }
    },
    methods: { // these methods are not cached
        reversedMessage: function () {
            return this.message.split('').reverse().join('')
        }
    },
    watch: { // observe and react to data changes, don't overuse
        capitalize: function () {
            return this.message.toUpperCase()
        }
    },
    template: '<span>{{ message }}</span>'
}
