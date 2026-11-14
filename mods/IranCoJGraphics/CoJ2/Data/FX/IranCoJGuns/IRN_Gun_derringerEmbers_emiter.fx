EmiterDef()
{
	Space("world")

	LifeTime()
	{
		keyf(0, 0.4)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 5)
	}

	StartVelocity()
	{
		keyf(0, 700)
	}

	StartVelocityRand()
	{
		keyv(0, 120, 260, 260)
	}

	Direction()
	{
		keyv(0, -1, 0, 0)
	}

	GenArea("point")
}
