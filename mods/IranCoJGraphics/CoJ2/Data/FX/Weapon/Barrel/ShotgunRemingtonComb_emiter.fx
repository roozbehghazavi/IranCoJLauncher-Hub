EmiterDef()
{
	Space("world")

	LifeTime()
	{
		keyf(0, 0.1)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 0)
	}

	StartVelocity()
	{
		keyf(0, 0)
	}

	StartVelocityRand()
	{
		keyv(0, 0, 0, 0)
	}

	Direction()
	{
		keyv(0, -1, 0, 0)
	}

	GenArea("point")
}
