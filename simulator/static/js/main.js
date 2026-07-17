particlesJS("particles-js", {

    particles: {

        number: {
            value: 90
        },

        color: {
            value: "#ffc107"
        },

        shape: {
            type: "circle"
        },

        opacity: {

            value: 0.5,

            random: true
        },

        size: {

            value: 4,

            random: true
        },

        move: {

            enable: true,

            speed: 2
        },

        line_linked: {

            enable: true,

            distance: 150,

            color: "#ffc107",

            opacity: 0.3,

            width: 1
        }

    },

    interactivity: {

        detect_on: "canvas",

        events: {

            onhover: {

                enable: true,

                mode: "repulse"
            },

            onclick: {

                enable: true,

                mode: "push"
            }

        }

    }

});